from typing import List, Optional, Tuple, Dict
import sqlalchemy as db, os
import requests, json, random, os
from requests.exceptions import ConnectionError, ConnectTimeout, SSLError, RequestException, HTTPError, ProxyError, Timeout, ReadTimeout, JSONDecodeError, TooManyRedirects, ChunkedEncodingError
from .Typer import Typer, Color
#from deskaone_sdk_scrypt_2023 import Typer, Color
from bs4 import BeautifulSoup
from sqlalchemy import BOOLEAN, INTEGER, VARCHAR, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from deskaone_sdk_scrypt_2023.Exceptions import Error
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
Base = declarative_base()

class __DB__:
    
    class Connection:
        
        def __init__(self, DATABASE_NAME: str) -> None:
            if os.path.exists('Database') is False:
                os.mkdir('Database')
            __engine      = create_engine(f'sqlite:///Database/{DATABASE_NAME}.db', echo=False)        
            __metadata    = MetaData()
            __engine.connect()
            try:Base.metadata.create_all(__engine)
            except Error as e:pass
            self.Engine      = __engine
            self.Metadata    = __metadata

class __ProxyBase__:
    
    class Base:
    
        def __init__(self) -> None:
            self.DB = __DB__.Connection('Proxy')
        
        class Proxy(Base):
            
            __tablename__   = 'Proxy'    
            id              = db.Column(INTEGER(), primary_key=True)
            country         = db.Column(VARCHAR(255), nullable=False)
            countryCode     = db.Column(VARCHAR(255), nullable=False)
            IpPort          = db.Column(VARCHAR(255), unique=True, nullable=False)
            Proxies         = db.Column(VARCHAR(255), nullable=False)
            BProgrammers    = db.Column(BOOLEAN(), nullable=False)
            Givvy           = db.Column(BOOLEAN(), nullable=False)
            Viker           = db.Column(BOOLEAN(), nullable=False)
            PlayFabapi      = db.Column(BOOLEAN(), nullable=False)
            Zebedee         = db.Column(BOOLEAN(), nullable=False)
        
            def __repr__(self) -> str:
                return  json.dumps(dict(
                    id              = self.id,
                    country         = self.country,
                    countryCode     = self.countryCode,
                    IpPort          = self.IpPort,
                    Proxies         = self.Proxies,
                    BProgrammers    = self.BProgrammers,
                    Givvy           = self.Givvy,
                    Viker           = self.Viker,
                    PlayFabapi      = self.PlayFabapi,
                    Zebedee         = self.Zebedee,
                ), indent=4)
    
    class Proxys:
        
        class Connection:
        
            def __init__(self) -> None:
                self.Func        = __ProxyBase__.Base()
                self.Con         = self.Func.DB
                self.Engine      = self.Con.Engine
                self.Metadata    = self.Con.Metadata
        
        class SaveProxy(Connection):
            
            def Set(self, *args, **kwargs):
                if kwargs.get('IpPort') is None or kwargs.get('IpPort') == '':raise Error('IpPort Required')
                Session     = sessionmaker(bind=self.Engine)
                Session.configure(bind=self.Engine)
                session     = Session()
                try:
                    ed_user = self.Func.Proxy(
                        country         = kwargs.get('country'),
                        countryCode     = kwargs.get('countryCode'),
                        IpPort          = kwargs.get('IpPort'),
                        Proxies         = json.dumps(kwargs.get('Proxies')) if type(kwargs.get('Proxies')) == dict else kwargs.get('Proxies'),
                        BProgrammers    = False if kwargs.get('BProgrammers') is None else kwargs.get('BProgrammers'),
                        Givvy           = False if kwargs.get('Givvy') is None else kwargs.get('Givvy'),
                        Viker           = False if kwargs.get('Viker') is None else kwargs.get('Viker'),
                        PlayFabapi      = False if kwargs.get('PlayFabapi') is None else kwargs.get('PlayFabapi'),
                        Zebedee         = False if kwargs.get('Zebedee') is None else kwargs.get('Zebedee'),
                    )
                    session.add(ed_user)
                    session.commit()
                    session.close()
                    return True
                except IntegrityError as e:
                    return False
                
            def Get(self):
                Session     = sessionmaker(bind=self.Engine)
                Session.configure(bind=self.Engine)
                session     = Session()
                result  = session.query(self.Func.Proxy).filter().all()
                session.close()
                return [dict(json.loads(str(Dict))) for Dict in result]

            def GetByIpPort(self, IpPort: str):
                if IpPort is None or IpPort == '':raise Error('IpPort Required')
                Session     = sessionmaker(bind=self.Engine)
                Session.configure(bind=self.Engine)
                session     = Session()
                result  = session.query(self.Func.Proxy).filter_by(IpPort=IpPort).first()
                session.close()
                return dict(json.loads(str(result)))
            
            def Up(self, IpPort: str, Values: dict):
                if IpPort is None or IpPort == '':raise Error('IpPort Required')
                Session     = sessionmaker(bind=self.Engine)
                Session.configure(bind=self.Engine)
                session     = Session()
                result  = session.query(self.Func.Proxy).filter_by(IpPort=IpPort).update(Values)
                session.commit()
                session.close()
                return result
        
            def Del(self, IpPort: str):
                if IpPort is None or IpPort == '':raise Error('IpPort Required')
                Session     = sessionmaker(bind=self.Engine)
                Session.configure(bind=self.Engine)
                session     = Session()
                result  = session.query(self.Func.Proxy).filter_by(IpPort=IpPort).delete()
                session.commit()
                session.close()
                return result
        
            def DelAll(self):
                Session     = sessionmaker(bind=self.Engine)
                Session.configure(bind=self.Engine)
                session     = Session()
                result  = session.query(self.Func.Proxy).filter().delete()
                session.commit()
                session.close()
                return result


class __WebShare__:
    
    def __init__(self, Authorization: str) -> None:
        self.BASE_URL   = 'https://proxy.webshare.io/api/v2/'
        self.HEADERS    = dict(Authorization = Authorization)
        self.Session    = requests.Session()
    
    @property
    def __proxy__(self) -> list:
        URL     = self.BASE_URL + 'proxy/list/?mode=direct&page=1&page_size=1000'
        Result  = self.Session.get(URL, headers=self.HEADERS).json()
        #json.dump(Result, open('webshare.json', 'w'), indent=4)
        return Result.get('results')
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            for Proxy in self.__proxy__:
                USERNAME        = Proxy.get('username')
                PASSWORD        = Proxy.get('password')
                IP              = Proxy.get('proxy_address')
                PORT            = Proxy.get('port')
                #ABC         = ['http', 'socks5']
                SCHEMA      = 'http'# ABC[random.randint(0, len(ABC) - 1)]
                try:
                    while True:
                        Set = __ProxyBase__.Proxys.SaveProxy().Set(
                            country         = '',
                            countryCode     = '',
                            IpPort          = f'{IP}:{PORT}',
                            Proxies         = dict(
                                http    = f'{SCHEMA}://{USERNAME}:{PASSWORD}@{IP}:{PORT}',
                                https   = f'{SCHEMA}://{USERNAME}:{PASSWORD}@{IP}:{PORT}',
                            ),
                            BProgrammers    = False,
                            Givvy           = False,
                            Viker           = False,
                            PlayFabapi      = False,
                            Zebedee         = False
                        )
                        if Set is False:
                            __ProxyBase__.Proxys.SaveProxy().Del(f'{IP}:{PORT}')
                        else: break
                            #__ProxyBase__.Proxys.SaveProxy().Up(
                            #    IpPort          = f'{IP}:{PORT}',
                            #    Values          = dict(
                            #        country         = '',
                            #        countryCode     = '',
                            #        Proxies         = dict(
                            #            http    = f'{SCHEMA}://{USERNAME}:{PASSWORD}@{IP}:{PORT}',
                            #            https   = f'{SCHEMA}://{USERNAME}:{PASSWORD}@{IP}:{PORT}',
                            #        ),
                            #        BProgrammers    = False,
                            #        Givvy           = False,
                            #        Viker           = False,
                            #        PlayFabapi      = False,
                            #        Zebedee         = False
                        #    )
                        #)
                except Error:pass
        return __ProxyBase__.Proxys.SaveProxy().Get()

class __ProxyScrape__:
    
    def __init__(self) -> None:
        self.Session    = requests.Session()
    
    @property
    def __proxy__(self):
        URL     = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all'
        Result  = self.Session.get(URL).text
        Saves = [Proxy for Proxy in Result.replace(' ', '').replace('\r', '').split('\n')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = Proxy,
                    Proxies         = dict(
                        http    = f'http://{Proxy}',
                        https   = f'http://{Proxy}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
        
        URL     = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all&ssl=all&anonymity=all'
        Result  = self.Session.get(URL).text
        Saves = [Proxy for Proxy in Result.replace(' ', '').replace('\r', '').split('\n')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = Proxy,
                    Proxies         = dict(
                        http    = f'socks4://{Proxy}',
                        https   = f'socks4://{Proxy}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
        
        URL     = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all&ssl=all&anonymity=all'
        Result  = self.Session.get(URL).text
        Saves = [Proxy for Proxy in Result.replace(' ', '').replace('\r', '').split('\n')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = Proxy,
                    Proxies         = dict(
                        http    = f'socks5://{Proxy}',
                        https   = f'socks5://{Proxy}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            self.__proxy__
        return __ProxyBase__.Proxys.SaveProxy().Get()
    
class __Geonode__:
    
    def __init__(self) -> None:
        self.Session    = requests.Session()
        self.BASE_URL   = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&speed=medium&protocols=http%2Chttps%2Csocks4%2Csocks5'
    
    @property
    def __proxy__(self):
        Result  = self.Session.get(self.BASE_URL).json()
        data    = list(Result.get('data'))
        Saves: List[dict] = [List for List in data]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            IP      = Proxy.get('ip')
            PORT    = Proxy.get('port')
            SCHEMA  = Proxy.get('protocols')[0]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'{SCHEMA.lower()}://{IP}:{PORT}',
                        https   = f'{SCHEMA.lower()}://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            self.__proxy__
        return __ProxyBase__.Proxys.SaveProxy().Get()
    
class __FreeProxyList__:
    
    def __init__(self) -> None:
        self.Session    = requests.Session()
        self.BASE_URL   = 'https://free-proxy-list.net/'
    
    @property
    def __proxy__(self):
        r  = self.Session.get(self.BASE_URL)
        Result = BeautifulSoup(r.content, 'html5lib')
        Saves = [List for List in Result.findAll('tbody')[0].findAll('tr')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            SPLIT   = str(Proxy).split('td>')
            IP      = SPLIT[1].split('</')[0]
            PORT    = SPLIT[3].split('</')[0]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'http://{IP}:{PORT}',
                        https   = f'http://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            self.__proxy__
        return __ProxyBase__.Proxys.SaveProxy().Get()
    
class __ProxyList__:
    
    def __init__(self) -> None:
        self.Session    = requests.Session()
    
    @property
    def __http__(self):
        r  = self.Session.get('https://www.proxy-list.download/HTTP')
        Result = BeautifulSoup(r.content, 'html5lib')
        Saves = [List for List in Result.findAll('tbody', attrs={'id': 'tabli'})[0].findAll('tr')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            SPLIT   = str(Proxy).split('td>')
            IP      = SPLIT[1].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            PORT    = SPLIT[3].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'http://{IP}:{PORT}',
                        https   = f'http://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
    
    @property
    def __https__(self):
        r  = self.Session.get('https://www.proxy-list.download/HTTPS')
        Result = BeautifulSoup(r.content, 'html5lib')
        Saves = [List for List in Result.findAll('tbody', attrs={'id': 'tabli'})[0].findAll('tr')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            SPLIT   = str(Proxy).split('td>')
            IP      = SPLIT[1].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            PORT    = SPLIT[3].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'http://{IP}:{PORT}',
                        https   = f'http://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
        
    @property
    def __socks4__(self):
        r  = self.Session.get('https://www.proxy-list.download/SOCKS4')
        Result = BeautifulSoup(r.content, 'html5lib')
        Saves = [List for List in Result.findAll('tbody', attrs={'id': 'tabli'})[0].findAll('tr')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            SPLIT   = str(Proxy).split('td>')
            IP      = SPLIT[1].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            PORT    = SPLIT[3].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'socks4://{IP}:{PORT}',
                        https   = f'socks4://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
        
    @property
    def __socks5__(self):
        r  = self.Session.get('https://www.proxy-list.download/SOCKS5')
        Result = BeautifulSoup(r.content, 'html5lib')
        Saves = [List for List in Result.findAll('tbody', attrs={'id': 'tabli'})[0].findAll('tr')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            SPLIT   = str(Proxy).split('td>')
            IP      = SPLIT[1].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            PORT    = SPLIT[3].replace(' ', '').replace('\n', '').replace('\r', '').split('</')[0]
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'socks5://{IP}:{PORT}',
                        https   = f'socks5://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
    
    @property
    def __proxy__(self):
        self.__http__
        self.__https__
        self.__socks4__
        self.__socks5__
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            self.__proxy__
        return __ProxyBase__.Proxys.SaveProxy().Get()

class __HideMy__:
    
    def First(self):
        URL = 'https://hidemy.name/en/proxy-list/'
        r = requests.get(URL, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'})
        return BeautifulSoup(r.content, 'html5lib')

    @property
    def __proxy__(self):
        SOUP = self.First()
        Saves = [List for List in SOUP.findAll('tbody')[0].findAll('tr')]
        for i in range(len(Saves)):
            Proxy = Saves[random.randint(0, len(Saves) - 1)]
            TD = str(Proxy).split('td>')
            IP = TD[1].split('</')[0]
            PORT = TD[3].split('</')[0]
            TYPE = 'http' if TD[9].split('</')[0].lower() == 'https' else TD[9].split('</')[0].lower()
            try:
                __ProxyBase__.Proxys.SaveProxy().Set(
                    country         = '',
                    countryCode     = '',
                    IpPort          = f'{IP}:{PORT}',
                    Proxies         = dict(
                        http    = f'{TYPE}://{IP}:{PORT}',
                        https   = f'{TYPE}://{IP}:{PORT}',
                    ),
                    BProgrammers    = False,
                    Givvy           = False,
                    Viker           = False,
                    PlayFabapi      = False,
                    Zebedee         = False
                )
                #if i == random.randint(3 if len(Saves) < 20 else 20, len(Saves) - 1): break
            except Error:pass
            
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            self.__proxy__
        return __ProxyBase__.Proxys.SaveProxy().Get()

class __PremiumProxy__:
    
    def __init__(self) -> None:
        self.__url__ = [
            "https://premiumproxy.net/anonymous-proxy-list",
            'https://premiumproxy.net/elite-proxy-list',
            'https://premiumproxy.net/http-proxy-list',
            'https://premiumproxy.net/https-ssl-proxy-list',
            'https://premiumproxy.net/mikrotik-proxy-list',
            'https://premiumproxy.net/socks-proxy-list',
            'https://premiumproxy.net/squid-proxy-list',
            'https://premiumproxy.net/transparent-proxy-list',
            'https://premiumproxy.net/top-country-proxy-list'
        ]
        self.__payload__={}
        self.__headers__ = {}        
    
    def __result__(self, url: str):
        response = requests.request("GET", url, headers=self.__headers__, data=self.__payload__)
        return BeautifulSoup(response.text, features='html.parser')
    
    def __parse__(self, Proxys: list, Result: BeautifulSoup):
        Saves   = [List for List in Result.findAll('tbody')[0].findAll('tr', attrs={'class': 'pp1x'})]
        for S in Saves:
            I_P = S.findAll('td', attrs={'colspan': 1})[0].findAll('font')
            SCHEMA = 'http' if S.findAll('td', attrs={'colspan': 1})[1].findAll('font')[0].text.lower() == 'https' else S.findAll('td', attrs={'colspan': 1})[1].findAll('font')[0].text.lower()
            Proxys.append(dict(
                http    = f'{SCHEMA}://{I_P[0].text}',
                https   = f'{SCHEMA}://{I_P[0].text}',
            ))
        return Proxys

    @property
    def __proxy__(self):
        Proxys = list()
        for url in self.__url__:
            Proxys = self.__parse__(Proxys, self.__result__(url))
        for proxy in Proxys:
            PR = proxy.get('http')
            if PR is None:
                PR = proxy.get('socks4')
                if PR is None:
                    PR = proxy.get('socks5')
                    if PR is None:
                        PR = ''
            try:
                IpPort  = str(PR).split('//')[1]
                __ProxyBase__.Proxys.SaveProxy().Set(
                        country         = '',
                        countryCode     = '',
                        IpPort          = f'{IpPort}',
                        Proxies         = proxy,
                        BProgrammers    = False,
                        Givvy           = False,
                        Viker           = False,
                        PlayFabapi      = False,
                        Zebedee         = False
                    )
            except Error:pass
            except:pass
    
    def Main(self, New: bool) -> List[Dict[str, str]]:
        if New is True:
            self.__proxy__
        return __ProxyBase__.Proxys.SaveProxy().Get()


class Proxy:
    
    def __init__(self, Authorization: Optional[str] = None, New = True, *args, **kwargs) -> None:
        if New is True:
            Typer.Print(f'{Color.RED}=> {Color.WHITE}Please Wait {Color.GREEN}Scraping New Proxy', Refresh=True)
            self.__get__(Authorization, New, **kwargs)
        
        if kwargs.get('DESKAONE') is True:
            PR = 'resi.proxyscrape.com:8000'
            US = '88slkvnrbz'
            PS = 'wwlkgj723d'
            PRX = dict(
                http    = f'http://{US}:{PS}@{PR}',
                https   = f'http://{US}:{PS}@{PR}',
            )
            __ProxyBase__.Proxys.SaveProxy().Set(
                country         = '',
                countryCode     = '',
                IpPort          = PR,
                Proxies         = PRX,
                BProgrammers    = False,
                Givvy           = False,
                Viker           = False,
                PlayFabapi      = False,
                Zebedee         = False
            )
        self.__Authorization__ = Authorization
        self.__New__ = New
        self.__kwargs__ = kwargs
        self.__args__ = args
    
    @classmethod
    def Rescan(cls, Authorization: Optional[str] = None, New = True, *args, **kwargs):
        return cls(Authorization, New, *args, **kwargs)
        
    def ProxyError(self, IpPort: Optional[str] = None, Add = False):
        if Add is True:
            open('Database/ProxyError.txt', 'a').write(f'{IpPort}\n')
        else:
            if os.path.exists('Database/ProxyError.txt') is True:
                return set(open('Database/ProxyError.txt').read().split())
            else:
                return set(list())
        
    def ProxyDetect(self, IpPort: Optional[str] = None, Add = False):
        if Add is True:
            open('Database/ProxyDetect.txt', 'a').write(f'{IpPort}\n')
        else:
            if os.path.exists('Database/ProxyDetect.txt') is True:
                return set(open('Database/ProxyDetect.txt').read().split())
            else:
                return set(list())
    
    @property
    def ListProxy(self) -> List[Dict[str, str]]:
        return __ProxyBase__.Proxys.SaveProxy().Get()
    
    def __get__(self, Authorization: Optional[str] = None, New = True, *args, **kwargs):
        if Authorization is not None and Authorization != '':__WebShare__(Authorization).Main(New)
        try:
            if kwargs.get('ProxyScrape') is True or kwargs.get('ProxyScrape') is None:__ProxyScrape__().Main(New)
        except:pass
        try:
            if kwargs.get('Geonode') is True or kwargs.get('Geonode') is None:__Geonode__().Main(New)
        except:pass
        try:
            if kwargs.get('FreeProxyList') is True or kwargs.get('FreeProxyList') is None:__FreeProxyList__().Main(New)
        except:pass
        try:
            if kwargs.get('ProxyList') is True or kwargs.get('ProxyList') is None:__ProxyList__().Main(New)
        except:pass
        try:
            if kwargs.get('HideMy') is True or kwargs.get('HideMy') is None:__HideMy__().Main(New)
        except:pass
        try:
            if kwargs.get('PremiumProxy') is True or kwargs.get('PremiumProxy') is None:__PremiumProxy__().Main(New)
        except:pass
    
    def __check__(self, *args, **kwargs):
        if kwargs.get('IpPort') is None: raise Error('IpPort Required')
        ListProxy, Count = self.ListProxy, 0
        while True:
            Count += 1
            try:
                ProxyErrorGO = False
                ProxyDetectGO = False
                PROXY   = ListProxy[random.randint(0, len(ListProxy) - 1)]
                IpPort = PROXY.get("IpPort")
                if IpPort in self.ProxyError(Add=False): ProxyErrorGO = True
                if IpPort in self.ProxyDetect(Add=False): ProxyDetectGO = True
                Typer.Print(f'{Color.RED}=> {Color.WHITE}Generate New Proxy {Color.GREEN}{PROXY.get("IpPort")} {Color.WHITE}Count {Color.GREEN}{Count}', Refresh=True) 
                if ProxyDetectGO is False and ProxyErrorGO is False:
                    if kwargs.get('IpPort') != PROXY.get("IpPort"):
                        API     = dict(requests.get("http://ip-api.com/json/%1s" % (PROXY.get('IpPort').split(":")[0])).json())
                        Typer.Print(f'{Color.RED}=> {Color.WHITE}Check New Proxy {Color.GREEN}{PROXY.get("IpPort")} {Color.WHITE}Country {Color.GREEN}{API.get("country")}', Refresh=True) 
                        MYIP    = dict(requests.get("https://kin4u.com/test").json())
                        S1 = requests.Session()
                        CHECK   = dict(S1.get("https://kin4u.com/test", proxies=PROXY.get('Proxies') if PROXY.get('Proxies') == dict else json.loads(PROXY.get('Proxies')), timeout=15).json())
                        if MYIP.get('HTTP_X_FORWARDED_FOR') != CHECK.get('HTTP_X_FORWARDED_FOR'):
                            S1.close()
                            __ProxyBase__.Proxys.SaveProxy().Up(IpPort = PROXY.get("IpPort"), Values = dict(countryCode = API.get("countryCode"), country = API.get("country")))
                            return dict(
                                PROXY   = PROXY.get('Proxies') if PROXY.get('Proxies') == dict else json.loads(PROXY.get('Proxies')),
                                DATA    = API,
                                IpPort  = PROXY.get('IpPort')
                            )
                if Count >= len(self.ListProxy):
                    self.Rescan(self.__Authorization__, self.__New__, *self.__args__, **self.__kwargs__)
            except ProxyError as e:
                self.ProxyError(IpPort=IpPort, Add=True)
            except ConnectTimeout as e:
                self.ProxyError(IpPort=IpPort, Add=True)
            except ConnectionError as e:
                self.ProxyError(IpPort=IpPort, Add=True)
            except ReadTimeout as e:
                self.ProxyError(IpPort=IpPort, Add=True)
            except JSONDecodeError:
                self.ProxyError(IpPort=IpPort, Add=True)
            except TooManyRedirects as e:
                self.ProxyError(IpPort=IpPort, Add=True)
            except Exception as e:
                self.ProxyError(IpPort=IpPort, Add=True)
    
    def Generate(self, *args, **kwargs) -> Tuple[bool, dict]:
        if len(self.ListProxy) != 0:return True,  self.__check__(**kwargs)
        return False, dict()
    
    def Show(self):
        return self.ListProxy
    
    def Random(self):
        return self.ListProxy[random.randint(0, len(self.ListProxy) - 1)]
    
    def Count(self):
        return len(self.ListProxy)
    
    def Get(self):
        _, Result = self.Generate()
        return Result
                