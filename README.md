ss-ssr-gadget
=======================
### ss2ssr.py 工具

批量将 ss:// 链接转换成 ssr:// 链接 uri 的工具，同时实现去重，查错，备份的功能。
支持 json文件，ss 原生 gui-config.json 账号配置文件，以及 ss:// uri 格式。三种用法：

*  $py ss2ssr.py -s #后接 ss:// 的链接，命令输出即为 ssr:// 链接，支持输入多个链接，空格隔开。与下面两个处理文件的参数互相排斥
*  $py ss2ssr.py -j #后接 json 文件或 ss 配置文件 gui-config.json，输出默认保存当前目录。支持以上两种文件、多文件混合合并输入
*  $py ss2ssr.py -l #后接 ss:// link 多个文件，空格隔开，文件格式要求为每行一个ss://记录，输出默认保存本地目录

支持同一个参数后接多文件，支持 -l 和 -j 同时使用，多个文件混合一起去重、备份，转换格式，支持多文件 * 通配符。-s 选项支持多链接。自动生成文件名类似 SS_to_SSR_links_2018-03-01_19-07-59.txt 的文件，文件内部是 ssr:// uri，每行一条记录。

### ssr-dup-remover.py 工具

支持批量去重、查错，备份处理 json 格式的 ssr 账户文件，包括 gui-config.json 和以列表-字典方式存储的 json 账户文件。
用法：

* $py ssr-dup-remover.py -j #后接 json 或 ssr gui-config.json 文件。支持混合多个文件输入。生成 "de_Dup_时间戳.json" 的去重文件，和 "Dup_时间戳.json" 的重复内容备份文件。如果没有输入-j 和 -o 文件参数，此命令会在当前目录下寻找名为 "gui-config.json" 的文件进行处理
* $py ssr-dup-remover.py -o #用来特别指定读取你正在使用的 ssr 配置文件，请使用此参数，配合 -j 同时使用，用来指定你已经在使用的 ssr gui-config.json 文件，这样将生成一个**替换掉**其中所有账户，而不修改其他配置，名为 "de_Dup_时间戳_gui-config.json" 的新配置文件，可以将其复制到 ssr 目录，重命名为 "gui-config.json" 即可使用。重复的账户将如前所述，生成名为 "Dup_时间戳.json 备份文件。
* $py ssr-dup-remover.py -t #同上命令，设置 -t 后只测试，不输出任何文件。

**建议用法**：将工具放置在 ssr 工作目录，运行，"$py ssr-dup-remover.py" 即可生成去重后的配置文件。备份或删除、重命名替换掉原来的配置文件 "gui-config.json" 即可应用。请注意**备份原配置文件**。
如果处理多个输入文件，必须 -j 和 -o （用来指定你现在使用的ssr配置文件）联合使用，才会生成 gui-config.json 配置文件，单独的 -j 只会生成去重的备份 json 文件。

其他工具待更新...
