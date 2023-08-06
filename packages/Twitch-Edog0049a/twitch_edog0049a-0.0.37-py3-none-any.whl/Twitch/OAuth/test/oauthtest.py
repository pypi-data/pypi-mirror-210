import asyncio
from Twitch import Oauth
from Twitch.secretkeys import apikeys

async def main():
    oauth = Oauth(apikeys.CLIENT_ID,apikeys.CLIENT_SECRET, "user:edit:follows",redirectUrl=None)
    while True:
        print("[TESTING OPTIONS]")
        print('(1) test oauth get tokenm with code')
        print('(2) test oauth validate token')
        print('(3) test oauth refresh token')
        print("(q) to quit")
        option = input("please select option: ")  
        if option == '1':
            token=""
            print(oauth.getCodeURL(""))
            code = input("plase paste code here: ")
            tokenobj = await oauth.getTokenFromCode(code)
            print(f'Access Token: {tokenobj.access_token}')
            print(f'Refresh Token: {tokenobj.refresh_token}')
            print(f'Scope: {tokenobj.scope}')
            token = tokenobj.access_token
            print(f'Token is valid:{await Oauth.vaidateToken(token)}')
        if option == '2':
            token = input('Please input token to validate:')
            print(f'Token is valid:{await Oauth.vaidateToken(token)}')

        if option == '3':
            token = input('Please input refresh token:')
            tokenobj = await oauth.refreshToken(token)
            print(f'Access Token: {tokenobj.access_token}')
            print(f'Refresh Token: {tokenobj.refresh_token}')
            print(f'Scope: {tokenobj.scope}')
        if option == 'q':
            break

if __name__=='__main__':
    asyncio.run(main())