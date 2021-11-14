# 🍃 Spotify – get a random saved album

1. Install dependencies:
	```sh
	pip install spotipy python-dotenv
	```
2. Login and create a new Spotify Developer app at https://developer.spotify.com/dashboard/applications
	![](pics/2021-11-14-17-30-46.png)

3. On the Dashboard open created app

4. Click `Edit settings` -> `Redirect URIs` -> add redirect URL `http://127.0.0.1:9090`
	![](pics/2021-11-14-17-36-37.png)

5. Copy `Client ID` and `Client Secret` from the app's main page
	![](pics/2021-11-14-17-32-40.png)

6. Create a new file `env` at the same directory level as `src.py`
	create `.env`
	replace `MY_CLIENT_ID` and `MY_CLIENT_SEC` with your values and append them to `.env`

	```bash
	touch .env
	echo "ID=MY_CLIENT_ID" >> .env
	echo "SEC=MY_CLIENT_SEC" >> .env
	cat .env
	```
	File `.env` should look like this:
	```
	ID=854c...
	SEC=e85e...
	```
7. Run `src.py` to get an external Spotify link to a random saved album
	```python
	python3 src.py
	```
You have to pass the OAuth via browser once on last step
