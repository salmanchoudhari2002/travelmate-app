from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.storage.jsonstore import JsonStore
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import mainthread
import requests
import os
import threading
import time

KV_PATH = os.path.join(os.path.dirname(__file__), 'kivy.kv')
KV = open(KV_PATH, 'r', encoding='utf8').read()

BACKEND = os.environ.get('TRAVEL_BACKEND_URL', 'http://127.0.0.1:8000')

# store local trips under project root local_store.json for portability
STORE_PATH = os.path.join(os.path.dirname(__file__), '..', 'local_store.json')
store = JsonStore(STORE_PATH)


class LoginScreen(Screen):
    def signup(self):
        email = self.ids.email.text.strip()
        pw = self.ids.password.text.strip()
        if not email or not pw:
            self.ids.msg.text = 'Email and password required'
            return
        try:
            r = requests.post(f"{BACKEND}/auth/signup", json={'email': email, 'password': pw}, timeout=8)
            if r.status_code == 200:
                tok = r.json().get('access_token')
                store.put('auth', token=tok, email=email)
                self.manager.current = 'trips'
            else:
                self.ids.msg.text = f'Error: {r.status_code} {r.text}'
        except Exception as e:
            self.ids.msg.text = f'Network error: {e}'

    def login(self):
        email = self.ids.email.text.strip()
        pw = self.ids.password.text.strip()
        if not email or not pw:
            self.ids.msg.text = 'Email and password required'
            return
        try:
            r = requests.post(f"{BACKEND}/auth/token", data={'username': email, 'password': pw}, timeout=8)
            if r.status_code == 200:
                tok = r.json().get('access_token')
                store.put('auth', token=tok, email=email)
                self.manager.current = 'trips'
            else:
                self.ids.msg.text = 'Login failed'
        except Exception as e:
            self.ids.msg.text = f'Network error: {e}'


class SearchScreen(Screen):
    def do_search(self):
        q = self.ids.q.text.strip()
        if not q:
            return
        self.ids.results.clear_widgets()
        self.ids.results.add_widget(Label(text='Searching...'))

        def _search():
            try:
                r = requests.get(f"{BACKEND}/map/search", params={'query': q, 'limit': 10}, timeout=8)
                data = r.json().get('results', []) if r.status_code == 200 else []
            except Exception:
                data = []
            self._show_results(data)

        threading.Thread(target=_search, daemon=True).start()

    @mainthread
    def _show_results(self, data):
        self.ids.results.clear_widgets()
        for it in data:
            btn = self.create_result_item(it)
            self.ids.results.add_widget(btn)

    def create_result_item(self, it):
        from kivy.uix.button import Button
        btn = Button(text=it.get('name') or it.get('display_name'), size_hint_y=None, height=48)

        def on_click(instance):
            self.manager.get_screen('newtrip').populate_from_place(it)
            self.manager.current = 'newtrip'

        btn.bind(on_release=on_click)
        return btn


class NewTripScreen(Screen):
    def populate_from_place(self, place):
        self.ids.dest.text = place.get('name') or place.get('display_name')
        self.ids.image_url.text = place.get('image') or ''

    def save_trip(self):
        dest = self.ids.dest.text.strip()
        mode = self.ids.mode.text.strip()
        try:
            expenses = float(self.ids.expenses.text or 0)
        except Exception:
            expenses = 0.0
        image_url = self.ids.image_url.text.strip() or None

        items = store.get('items')['items'] if store.exists('items') else []
        items.append({'destination': dest, 'mode': mode, 'expenses': expenses, 'synced': False, 'image_url': image_url})
        store.put('items', items=items)
        self.manager.current = 'trips'


class TripListScreen(Screen):
    def on_pre_enter(self):
        # populate local trips immediately
        self.populate_local()
        # if logged in, fetch remote
        if store.exists('auth'):
            token = store.get('auth').get('token')
            if token:
                threading.Thread(target=self.fetch_remote, args=(token,), daemon=True).start()
                # schedule a single delayed refresh to pick up thumbnails generated in background
                def delayed():
                    try:
                        time.sleep(8)
                        self.fetch_remote(token)
                    except Exception:
                        pass
                threading.Thread(target=delayed, daemon=True).start()

    @mainthread
    def populate_local(self):
        self.ids.trip_list.clear_widgets()
        items = store.get('items')['items'] if store.exists('items') else []
        for it in items:
            w = self.create_trip_widget(it, local=True)
            self.ids.trip_list.add_widget(w)

    def create_trip_widget(self, trip, local=False):
        box = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=8, padding=4)
        # image
        # prefer thumbnail if available
        img_src = trip.get('thumbnail') or trip.get('image_url')
        # If backend returned a relative path like '/static/images/..', make it absolute so AsyncImage can load it
        if img_src and img_src.startswith('/'):
            img_src = BACKEND.rstrip('/') + img_src
        if img_src:
            img = AsyncImage(source=img_src, size_hint=(None, 1), width=160)
        else:
            img = Label(text='No image', size_hint=(None, 1), width=160)
        box.add_widget(img)
        # details
        details = BoxLayout(orientation='vertical')
        details.add_widget(Label(text=str(trip.get('destination') or ''), halign='left'))
        details.add_widget(Label(text=f"Mode: {trip.get('mode')}", halign='left'))
        details.add_widget(Label(text=f"Expenses: {trip.get('expenses')}", halign='left'))
        box.add_widget(details)
        return box

    def fetch_remote(self, token):
        try:
            r = requests.get(f"{BACKEND}/trips/", headers={'Authorization': f'Bearer {token}'}, timeout=8)
            if r.status_code == 200:
                data = r.json()
            else:
                data = []
        except Exception:
            data = []
        self._show_remote(data)

    @mainthread
    def _show_remote(self, data):
        # append remote trips below local ones
        for it in data:
            w = self.create_trip_widget(it, local=False)
            self.ids.trip_list.add_widget(w)

    def do_sync(self):
        if not store.exists('auth'):
            self.ids.sync_msg.text = 'Login required to sync'
            return
        token = store.get('auth').get('token')
        if not token:
            self.ids.sync_msg.text = 'Login required to sync'
            return

        items = store.get('items')['items'] if store.exists('items') else []
        unsynced = [t for t in items if not t.get('synced')]
        if not unsynced:
            self.ids.sync_msg.text = 'No unsynced trips'
            return

        payload = []
        for t in unsynced:
            cleaned = {k: v for k, v in t.items() if k in ('start_lat','start_lng','destination','mode','start_date','end_date','expenses','purpose','notes','image_url')}
            payload.append(cleaned)

        try:
            r = requests.post(f"{BACKEND}/trips/sync", json=payload, headers={'Authorization': f'Bearer {token}'}, timeout=10)
            if r.status_code == 200:
                # mark local as synced
                for it in items:
                    it['synced'] = True
                store.put('items', items=items)
                self.ids.sync_msg.text = 'Sync successful'
                self.populate_local()
            else:
                self.ids.sync_msg.text = f'Sync failed: {r.status_code}'
        except Exception as e:
            self.ids.sync_msg.text = f'Network error: {e}'


class RootApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SearchScreen(name='search'))
        sm.add_widget(NewTripScreen(name='newtrip'))
        sm.add_widget(TripListScreen(name='trips'))
        # start on trips (shows local) so images are visible immediately
        sm.current = 'trips'
        return sm


if __name__ == '__main__':
    RootApp().run()
