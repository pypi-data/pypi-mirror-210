## 简介
asa自用的工具包，功能包括
- bira 下载b站视频
    - 需要配置conf.ini，格式为
        ```ini
        [spiderbi] 
        SESSDATA = "XXXX"
        ```
    - 需要环境变量中配置ASA_HOME
- cf    copyFolder 复制所有源代码文件到asahome的文件夹下
- cp4   mp4拷贝到asa_home的环境变量的目录中，并重命名为合法字符
- ctt   mp4目录下文件生成要转换的txt文件
- od    调用out_dutys 转换值班为js
- ra    removeAnnotate 去掉注解
- ttm4  合并mp4视频，转为h264编码mp4或海信电视可播放的mp4 equipment ： --e