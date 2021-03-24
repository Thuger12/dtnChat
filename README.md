### DTN chat(don't tell nobody). Toy chat.

* STATUS: not ready
* DTN is chat written in python and fully asynchronious.  
* Key idea is to work with SOCKET and ASYNCIO in python to make it as minimal as possible.
### Features
 * Chat got minimal, but full functionality
  
##### Pure asyncio socket implementation for registration and login(session key)

  >We implement pure socket to make it easy to work exactly with bytes. 
In the future it will be easy to deal with some security
  >Main server for logic implementation(aiohttp)
  >To work with API and websocket(for real time connection)
  >Make client part interactive and real time. Got some THREADING to hide blocking socket problem
