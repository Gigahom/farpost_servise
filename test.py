# Парсинг тестовой строки с HTTP заголовками
test_string = """
GET / HTTP/1.1
Host: www.farpost.ru
Cookie: ring=dc47a82a9e8b402de93919f2110d9340; boobs=797ae541601ec8f50da01020d0611ed293ab089d65d81aa490f8c77f46232611u16fd509; pony=4d6a51784d4459794e446b3ducf2add47fb05cf4f886a6ae3be29039b; login=79246763737; _ga_64RVG4FR1N=GS1.2.1705752945.1.0.1705752967.0.0.0; _ga=GA1.1.1205983125.1705675536; _ga_98VH35E9J1=GS1.1.1705845544.1.0.1705845544.60.0.0; _ga_G0RWKN84TQ=GS1.1.1705845538.3.1.1705846718.29.0.0
Sec-Ch-Ua: 
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Full-Version: ""
Sec-Ch-Ua-Arch: ""
Sec-Ch-Ua-Platform: ""
Sec-Ch-Ua-Platform-Version: ""
Sec-Ch-Ua-Model: ""
Sec-Ch-Ua-Bitness: ""
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36
Sec-Purpose: prefetch;prerender
Purpose: prefetch
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: none
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate
Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7
Connection: close
"""



headers, cookeis = parse_http_headers(test_string)



print(cookeis)
print(headers)

