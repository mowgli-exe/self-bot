https://discord.gg/36EAyW5Z4F
no support for retarded ppl btw 
> [!WARNING]
> **I don't take any responsibility for blocked Discord accounts that used this module.**

> [!CAUTION]
> **Using this on a user account is prohibited by the [Discord TOS](https://discord.com/terms) and can lead to the account block.**

## Features (User)
- [x] Auto Message
- [x] Auto Mute for 30 sec ( protect for spammer ) 
- [X] .ban (ping user ) and for unbann .unban (user) @ Only Owner can do that.
- [X] .ping @ Owner Only can do that

## Installation

> [!NOTE]
> **python*

## Get Token ?

- open discord  in web and run code in below 

<strong>Run code (Discord Console - [Ctrl + Shift + I])</strong>

```js
window.webpackChunkdiscord_app.push([
	[Symbol()],
	{},
	req => {
		if (!req.c) return;
		for (let m of Object.values(req.c)) {
			try {
				if (!m.exports || m.exports === window) continue;
				if (m.exports?.getToken) return copy(m.exports.getToken());
				for (let ex in m.exports) {
					if (m.exports?.[ex]?.getToken && m.exports[ex][Symbol.toStringTag] !== 'IntlMessagesProxy') return copy(m.exports[ex].getToken());
				}
			} catch {}
		}
	},
]);

window.webpackChunkdiscord_app.pop();
console.log('%cWorked!', 'font-size: 50px');
console.log(`%cYou now have your token in the clipboard!`, 'font-size: 16px');
```
- you can use https://railway.com/ or others. ( You NEED add In variables DISCORD_TOKEN and add youre Discord Token in there ) 
## Star History
Please give it a star if you like that ( https://github.com/mowgli-exe/self-bot/ )
