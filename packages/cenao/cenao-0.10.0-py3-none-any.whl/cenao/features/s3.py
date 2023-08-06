from typing import Any, Dict, Optional

import aiohttp
import datetime
import hashlib
import hmac
import urllib.parse

from cenao.app import AppFeature


class S3Client:
    _endpoint: str
    _region: str
    _bucket: str
    _access: str
    _secret: str
    _session: aiohttp.ClientSession

    _empty_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def __init__(self, endpoint: str, region: str, bucket: str, access: str, secret: str):
        self._endpoint = endpoint
        self._region = region
        self._bucket = bucket
        self._access = access
        self._secret = secret

        self._session = aiohttp.ClientSession()

    async def download_data(self, key: str) -> bytes:
        path = f'/{self._bucket}/{key}'
        headers = self._sign(path=path, method="GET")
        resp = await self._session.get(
            url=f'https://{self._endpoint}{path}',
            headers=headers
        )

        resp.raise_for_status()

        data = await resp.read()
        return data

    async def upload_data(self, key: str, payload: bytes):
        path = f'/{self._bucket}/{key}'
        headers = self._sign(path=path, method='PUT', payload=payload)
        resp = await self._session.put(
            url=f'https://{self._endpoint}{path}',
            headers=headers,
            data=payload
        )
        resp.raise_for_status()

    def _sign(
        self,
        path: str,
        method: str,
        payload: Optional[bytes] = None,
        content_type: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        if headers is None:
            headers = {}

        if query is None:
            query = {}

        now = datetime.datetime.utcnow()
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')

        payload_hash = hashlib.sha256(payload).hexdigest() if payload else None

        _headers = {
            **headers,
            'Host': self._endpoint,
            'x-amz-date': amz_date,
            "x-amz-content-sha256": payload_hash if payload_hash else self._empty_sha256
        }

        if payload_hash:
            _headers['x-amz-content-sha256'] = payload_hash

        if content_type:
            _headers['Content-Type'] = content_type

        sorted_headers = {}
        for item in sorted(_headers.keys()):
            sorted_headers[item] = _headers[item]

        canonical_uri = urllib.parse.quote(path, safe='/~')
        quoted_query = sorted(
            (urllib.parse.quote(key, safe='~'), urllib.parse.quote(value, safe='~'))
            for key, value in query.items()
        )
        canonical_querystring = '&'.join(f'{key}={value}' for key, value in quoted_query)
        canonical_headers = ''.join(
            f'{key.lower()}:{sorted_headers[key]}\n' for key in sorted_headers.keys()
        )

        signed_headers_str = ';'.join(sorted_headers.keys()).lower()
        canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n' + \
                            f'{canonical_headers}\n{signed_headers_str}\n'
        canonical_request += payload_hash if payload_hash else self._empty_sha256

        def sign(key, msg):
            return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

        datestamp = now.strftime('%Y%m%d')
        credential_scope = f'{datestamp}/{self._region}/s3/aws4_request'
        string_to_sign = f'AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n' + \
                         hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

        date_key = sign(('AWS4' + self._secret).encode('utf-8'), datestamp)
        region_key = sign(date_key, self._region)
        service_key = sign(region_key, 's3')
        request_key = sign(service_key, 'aws4_request')
        signature = sign(request_key, string_to_sign).hex()

        resp = {
            **sorted_headers,
            'Authorization': f'AWS4-HMAC-SHA256 Credential={self._access}/{credential_scope}, '
                             f'SignedHeaders={signed_headers_str}, Signature=' + signature,
        }

        return resp

    async def close(self):
        if self._session:
            await self._session.close()


class S3AppFeature(AppFeature):
    NAME = 's3'

    client: S3Client

    async def on_startup(self):
        self.client = S3Client(
            endpoint=self.config.get('endpoint'),
            region=self.config.get('region', 'us-east-1'),
            bucket=self.config.get('bucket'),
            access=self.config.get('access'),
            secret=self.config.get('secret'),
        )

    async def on_shutdown(self):
        if self.client:
            await self.client.close()
