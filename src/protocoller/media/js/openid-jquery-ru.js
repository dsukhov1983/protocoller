/*
	Simple OpenID Plugin
	http://code.google.com/p/openid-selector/
	
	This code is licenced under the New BSD License.
*/

var providers_large = {
	yandex : {
		name : 'Яндекс',
		url : 'http://openid.yandex.ru'
	},
	rambler : {
		name : 'Рамблер',
		url : 'http://www.rambler.ru'
	},
	google : {
		name : 'Google',
		url : 'https://www.google.com/accounts/o8/id'
	}
};

var providers_small = {
	openid : {
		name : 'OpenID',
		label : 'Введите ваш OpenID.',
		url : null
	},
	livejournal : {
		name : 'Живой Журнал',
		label : 'Введите ваше имя в Живом Журнале.',
		url : 'http://{username}.livejournal.com/'
	},
	flickr : {
		name : 'Flickr',
		label : 'Введите ваше имя на Flickr.',
		url : 'http://flickr.com/{username}/'
	},
	blogger : {
		name : 'Blogger',
		label : 'Ваш Blogger аккаунт',
		url : 'http://{username}.blogspot.com/'
	}
};

openid.lang = 'ru';
openid.demo_text = 'В демонстрационном режиме на клиенте. В действительности произошел бы сабмит следующего OpenID:';
openid.signin_text = 'Войти';
openid.image_title = 'войти c {provider}';
