import requests
import pandas as pd

SERVER_URL = "http://127.0.0.1:5555"

class Userbase:
    @staticmethod
    def check_sign_up(email: str, username: str, password: str):
        response = requests.post(
            url=f"{SERVER_URL}/sign_up",
            params={"email": email, "username": username, "password": password}
        )
        return response
    
    @staticmethod
    def check_check_sign_up():
        params = "ofekgrun@gmail.com", 12345, 12345
        try:
            print(f"Checking...")
            reseponse = Userbase.check_sign_up(params[0], params[1], params[2])
            print(f"response: {reseponse.status_code}, {reseponse.json()}")
        except Exception as error:
            print(f"error: {error}")


class Stocks:
    @staticmethod
    def pull_stock_from_server():
        response = requests.get(f"{SERVER_URL}/stock_data")
        try:
            print(f"Request: {response.status_code}\n")
            json: dict = response.json()
            print(type(json))
            print("\n\n\n\n\n\n")
            df = pd.DataFrame.from_dict(json, orient="columns")
            print(df)
        except Exception as error:
            print(f"own Error: {error}")
        

if __name__ == "__main__":
    Stocks.pull_stock_from_server()
