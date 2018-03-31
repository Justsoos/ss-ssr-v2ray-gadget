ss-ssr-v2ray-gadget
=======================
## ss2ssr.py 工具

批量将 ss:// 链接，或者 shadowsocks 的config文件内账号，转换成 ssr:// 链接 uri 的工具，同时实现去重，查错，备份的功能。
支持 json文件，ss 原生 gui-config.json 账号配置文件，以及 ss:// uri 格式。三种用法：

*  $py ss2ssr.py -s #后接 ss:// 的链接，命令输出即为 ssr:// 链接，支持输入多个链接，空格隔开。与下面两个处理文件的参数互相排斥
*  $py ss2ssr.py -j #后接 json 文件或 ss 配置文件 gui-config.json，输出默认保存当前目录。支持以上两种文件、多文件混合合并输入
*  $py ss2ssr.py -l #后接 ss:// link 多个文件，空格隔开，文件格式要求为每行一个ss://记录，输出默认保存本地目录

支持同一个参数后接多文件，支持 -l 和 -j 同时使用，多个文件混合一起去重、备份，转换格式，支持多文件 * 通配符。-s 选项支持多链接。自动生成文件名类似 SS_to_SSR_links_2018-03-01_19-07-59.txt 的文件，文件内部是 ssr:// uri，每行一条记录。

## ssr_dup_remover.py 工具

支持批量去重、查错，备份处理 json 格式的 ssr 账户文件，包括 gui-config.json 和以列表-字典方式存储的 json 账户文件。
用法：

* $py ssr_dup_remover.py -j #输入文件选项。后接 json 或 ssr gui-config.json 文件。支持混合多个文件输入。生成 "de_Dup_时间戳.json" 的去重文件，和 "Dup_时间戳.json" 的重复账号备份文件。如果没有输入-j 和 -o 文件参数，此命令会在当前目录下寻找名为 "gui-config.json" 的文件进行处理
* $py ssr_dup_remover.py -o #指定模板选项。读取你正在使用的 ssr 配置文件，使用此参数，要配合 -j 同时使用，用来指定你已经在使用的 ssr gui-config.json 文件，这样将生成一个**替换掉**其中所有账户，而不修改其他配置，名为 "de_Dup_时间戳_gui-config.json" 的新配置文件，可以将其复制到 ssr 目录，重命名为 "gui-config.json" 即可使用。重复的账户将如前所述，生成名为 "Dup_时间戳.json 备份文件
* $py ssr_dup_remover.py -t #设置 -t 后只测试，不输出任何文件

**建议用法**：将工具放置在 ssr 工作目录，无参数运行，"$py ssr_dup_remover.py" 即可生成去重后的配置文件。备份或删除、重命名替换掉原来的配置文件 "gui-config.json" 即可应用。请注意**备份原配置文件**。
如果处理多个输入文件，必须 -j 和 -o （用来指定你现在使用的ssr配置文件）联合使用，才会生成 gui-config.json 配置文件，单独的 -j 只会生成去重的备份 json 文件 -- 这个文件不能直接作为 ssr 配置文件应用。

## check_v2ray.py 工具

配合 [v2ray](https://github.com/v2ray), [v2rayN https://github.com/2dust/v2rayN](https://github.com/2dust/v2rayN) 使用，多进程，对账号批量去重，测试，benchmark。
使用很简单，放置文件 check_v2ray.py 到 v2rayN 目录（关闭 v2rayN 和 v2ray 与否都没问题，脚本会主动关闭），**以管理员或等同身份**执行，将生成一个包含去重、测速后的 guiNConfig_2018-xxxxxx_.json 带时间戳的配置文件，把原文件备份，删除，将此文件改名为 guiNConfig.json。重新运行 v2rayN.exe
可以看到每个账号别名前面都加上了类似这样的数字：
* 0_0.68_ 这表示，经过10次连接到 Google 首页的测速，其中0次 (第一个数字) 连接失败，平均每次获取 Google 的302首页需要0.68秒 （第二个数字）
* 或者 9_9.99_HCR_，这表示，10次连接都没有成功，这个节点暂时无法使用（被反科学上网了），或者已经废弃。
简单方便，选择数字最小的去使用就好了！

命令选项使用：
* -j选项，后接 json 格式配置文件名，支持多文件合并处理
* -t选项，只测试，不保存文件

暂时不支持 v2ray 下使用的 shadowsocks 账号。
建议你 将 ss 导入到 ssr 下使用，ssr-csharp 有更强大的内置数据支持，参考这里: 
[shadowsocksrr/shadowsocksr-csharp#33 (comment)](https://github.com/shadowsocksrr/shadowsocksr-csharp/issues/33#issuecomment-355440457)

ss, ssr 的配置文件是扁平的，uri 也简单粗放，所有数据都可以列在一个二层树上列出来，v2ray 则完全不同，即便 v2rayN 用一个二层树文件，凑合表达，造成不同语义复用键值，而且没有一个通用标准配置文件可用。[逻辑很乱，感觉还需要改很多 ...](https://github.com/v2ray/v2ray-core/issues/990)

* v2ray(N) Windows 客户端，推荐用这个：https://github.com/Jrohy/v2rayN 有很多方便的新功能，开发改造还很活跃。
* v2ray Android 客户端，推荐用这个：https://play.google.com/store/apps/details?id=com.github.dawndiy.bifrostv 不仅支持 socks5 协议代理，还有很多方便好用的功能。

## Winhttp_tools: M$ windows ~~系统~~ WinHTTP 代理取消、设置、显示，方便的鼠标敲一下就搞定的命令行

由于众多软件设计的美国佬的~~不知道网络审查而自由的富贵病~~ 微软、Google 大企业病，chrome browser 访问网站，[更新，内置 google translate 三件简单的事，能搞成九件事](https://docs.google.com/document/d/e/2PACX-1vTMoDzlLl3wgJSd4PcrLhVUeAOCid1XFtIOvrWHIONbf-AHMfGhhCxFna_kG3UlAZiE4pr-YnvwxaGw/pub)，加上 DNS poison，复杂度翻一倍，乱！~~只~~走winhttp，wininet系统代理，[很多人迷惑为什么我设置了 chrome 的 http 和 socks 代理，却无法升级 chrome ？不能用 chrome 内置的 google 翻译？](https://github.com/feliscatus/switchyomega/issues/264) 是的，你需要设置 windows 系统代理(而且还是相当乱套的好几个代理...)，这些独立于浏览器之外进程需要走~~系统~~代理，他们并不走浏览器内设置的代理。

其他工具待更新...
