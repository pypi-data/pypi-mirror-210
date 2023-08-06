import requests
import time
from urllib.parse import urlencode
import base64
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
class IG_Verify():

    def Dual_tokens(self):
        while True:
            try:
                data = urlencode({
                    'normal_token_hash': '',
                    'device_id': str(self.AndroidID),
                    'custom_device_id': str(self.IgDeviceId),
                    'fetch_reason': 'token_expired',
                })
                headers = {
                    'Host': 'b.i.instagram.com',
                    'X-Ig-App-Locale': 'en_US',
                    'X-Ig-Device-Locale': 'en_US',
                    'X-Ig-Mapped-Locale': 'en_US',
                    'X-Pigeon-Session-Id': str(self.PigeonSession),
                    'X-Pigeon-Rawclienttime': str(round(time.time(), 3)),
                    'X-Ig-Bandwidth-Speed-Kbps': '-1.000',
                    'X-Ig-Bandwidth-Totalbytes-B': '0',
                    'X-Ig-Bandwidth-Totaltime-Ms': '0',
                    'X-Bloks-Version-Id': str(self.Blockversion),
                    'X-Ig-Www-Claim': '0',
                    'X-Bloks-Is-Layout-Rtl': 'false',
                    'X-Ig-Device-Id': str(self.IgDeviceId),
                    'X-Ig-Android-Id': str(self.AndroidID),
                    'X-Ig-Timezone-Offset': '-18000',
                    'X-Fb-Connection-Type': 'WIFI',
                    'X-Ig-Connection-Type': 'WIFI',
                    'X-Ig-Capabilities': '3brTv10=',
                    'X-Ig-App-Id': '567067343352427',
                    'Priority': 'u=3',
                    'User-Agent': str(self.UserAgent),
                    'Accept-Language': 'en-US',
                    'Ig-Intended-User-Id': '0',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Content-Length': str(len(data)),
                    'Accept-Encoding': 'gzip, deflate',
                    'X-Fb-Http-Engine': 'Liger',
                    'X-Fb-Client-Ip': 'True',
                    'X-Fb-Server-Cluster': 'True',
                    'Connection': 'close',
                }
                response = requests.post('https://b.i.instagram.com/api/v1/zr/dual_tokens/', headers=headers, data=data, proxies=self.proxy)
                self.mid=response.headers['ig-set-x-mid']

                data = urlencode({
                    'params': '{"show_internal_settings":false,"offline_experiment_group":"caa_iteration_v3_perf_ig_4","device_id":"'+str(self.AndroidID)+'","logged_out_user":"","qe_device_id":"'+str(self.IgDeviceId)+'","qpl_join_id":"'+str(self.Qpl)+'","family_device_id":"'+str(self.IgFamilyDeviceId)+'","waterfall_id":"'+str(self.Waterfall)+'","account_list":[{"token":"","account_type":"google_oauth"}],"blocked_uid":[],"INTERNAL_INFRA_THEME":"default"}',
                    'bk_client_context': '{"bloks_version":"'+str(self.Blockversion)+'","styles_id":"instagram"}',
                    'bloks_versioning_id': str(self.Blockversion),
                })

                updict = {
                    "Content-Length":str(len(data)),
                    'Host': 'i.instagram.com',
                    'X-Mid': str(self.mid),
                    'X-Ig-Family-Device-Id': str(self.IgFamilyDeviceId),
                    'X-Pigeon-Rawclienttime': str(round(time.time(), 3)),


                          }
                headers = {key: updict.get(key, headers[key]) for key in headers}
                headers.update({'X-Tigon-Is-Retry': 'True',})


                response = requests.post(
                    'https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.bloks.caa.login.process_client_data_and_redirect/',
                    headers=headers,
                    data=data,
                    proxies=self.proxy,
                )

                self.emlogin=response.text.split('"K":"email","!":"')[1].split('","":[{"㚱":{"9":"","2":""}}]')[0]
                self.pwlogin = response.text.split('"K":"password","!":"')[1].split('","":[{"㚱":{"9":"","2":""}}]')[0]
                self.instance_id = response.text.split(', (bk.action.i32.Const, 2), (bk.action.tree.Make, (bk.action.i32.Const, 13704))))), (bk.action.i32.Const, 35), (bk.action.core.FuncConst, (bk.action.core.TakeLast, (bk.action.qpl.MarkerPoint, (bk.action.i32.Const, 36707139), (bk.action.i32.Const, ')[1].split(r'), \"handle_async_action_result_start\", (bk.action.tree.Make, (bk.action.i32.Const, 13747))), (bk.action.core.TakeLast, (bk.action.core.TakeLast, (bk.action.bloks.WriteLocalState, \"')[0]
                self.marker_id = response.text.split(r'\")))), (bk.action.core.TakeLast, (bk.action.bloks.WriteGlobalConsistencyStore, \"CAA_LOGIN_FORM:is_login_pending:0\", (bk.action.bool.Const, true)), (bk.action.core.TakeLast, (bk.action.qpl.MarkerStartV2, (bk.action.i32.Const, ')[1].split('), (bk.action.i32.Const, ')[0]



                return headers,self.mid,self.instance_id,self.marker_id,self.emlogin,self.pwlogin
            except Exception as E:
                print(E)


    def Dual_tokens2(self):
        while True:
            try:

                data = urlencode({
                    'normal_token_hash': '',
                    'device_id': str(self.AndroidID ),
                    '_uuid': str(self.IgDeviceId),
                    'custom_device_id': str(self.IgDeviceId),
                    'fetch_reason': 'token_expired',
                })

                self.headers.update({
                    'Authorization': f'Bearer IGT:2:{self.bearer}',
                    'Ig-U-Ds-User-Id': str(self.UserId),
                    'Ig-U-Rur': self.rur,
                                     })

                updict = {
                    "Content-Length": str(len(data)),
                    'X-Pigeon-Rawclienttime': str(round(time.time(), 3)),
                    'Ig-Intended-User-Id': str(self.UserId),
                    'Host': 'b.i.instagram.com',

                }
                self.headers = {key: updict.get(key, self.headers[key]) for key in self.headers}
                response = requests.post('https://b.i.instagram.com/api/v1/zr/dual_tokens/', headers=self.headers, data=data,
                                         proxies=self.proxy)
                self.claim=response.headers['x-ig-set-www-claim']
                self.shbid=response.headers['ig-set-ig-u-shbid']
                self.shbts=response.headers['ig-set-ig-u-shbts']
                self.urur=response.headers['ig-set-ig-u-rur']

                return self.claim,self.shbid,self.shbts,self.urur
            except Exception as E:
                print(E)

    def Enc_Passwd(self):
        while True:
            try:

                resp = requests.get('https://i.instagram.com/api/v1/qe/sync/',proxies=self.proxy)
                publickeyid = int(resp.headers.get('ig-set-password-encryption-key-id'))
                publickey = resp.headers.get('ig-set-password-encryption-pub-key')
                session_key = get_random_bytes(32)
                iv = get_random_bytes(12)
                timestamp = str(int(time.time()))
                decoded_publickey = base64.b64decode(publickey.encode())
                recipient_key = RSA.import_key(decoded_publickey)
                cipher_rsa = PKCS1_v1_5.new(recipient_key)
                rsa_encrypted = cipher_rsa.encrypt(session_key)
                cipher_aes = AES.new(session_key, AES.MODE_GCM, iv)
                cipher_aes.update(timestamp.encode())
                aes_encrypted, tag = cipher_aes.encrypt_and_digest(self.passw.encode("utf8"))
                size_buffer = len(rsa_encrypted).to_bytes(2, byteorder='little')
                payload = base64.b64encode(b''.join([
                    b"\x01",
                    publickeyid.to_bytes(1, byteorder='big'),
                    iv,
                    size_buffer,
                    rsa_encrypted,
                    tag,
                    aes_encrypted
                ]))
                return f'#PWD_INSTAGRAM:4:{timestamp}:{payload.decode()}'
            except Exception as E:
                print(E)



