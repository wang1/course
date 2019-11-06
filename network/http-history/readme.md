# HTTP发展

## HTTP1.0

### 原始HTTP

1996年`HTTP1.0`规范的发布, 该规范定义了我们今天所知道的基本`HTTP`文本传输格式(假装`HTTP0.9`不存在:). 

在`HTTP1.0`中, 需要为客户端和服务器之间的每个请求/响应交换创建一个新的`TCP`连接, 这意味着所有`TCP/TLS`握手均在每个请求之前完成, 因此所有请求都会产生延迟. 如下图所示.

![HTTP1.0连接及传输示意](./http1.0.png)

### HTTP1.1

> TCP使用了称为"`慢启动Slow Start`"的预热时间用于拥塞控制, "慢启动Slow Start"使TCP拥塞控制算法可以确定可以传输的数据量, 而不是在建立连接后尽快发送所有未完成的数据.

> 在网络路径上发生拥塞之前的任何给定时刻, 并避免将无法处理的数据包泛洪到网络中. 但是由于新连接必须经过缓慢的启动过程, 因此它们无法立即使用所有可用的网络带宽.

1999年1.1出现
HTTP刚诞生的时候只被当作是一个相对简单直观的协议，但时间证明了早期的设计并不尽人意。于1996年发布的、描述HTTP 1.0规范的RFC 1945只有60页，但仅仅3年之后、描述HTTP 1.1规范的RFC 2616就一下增长到了176页。
正式版http2规格标准叫做RFC 7540，发布于2015年5月15日

> ## 参考

1. https://mojotv.cn/cloudflare-http3-pass-present-future

1. https://http2-explained.haxx.se/content/zh/part3.html

2. https://http3-explained.haxx.se/zh/


            $(function() {
                $(window).ready(function() {
                    $.ajax({
                        type: "get",
                        url: "action.php",
                        success: function(data) {
                            $(".table-two").text(data);
                        },
                        error: function() {
                            console.log("Error Reading Data");
                        },
                        dataType: "json",
                        async: true
                    });
                });
            });

            $.get('Scripts/data.txt').success(function(content){
// content就为文件data.txt的文本内容了,注意txt文件的编码需要与html文件的编码一致，最好保存成utf-8
});

function getRandomLine(filename){
  fs.readFile(filename, function(err, data){
    if(err) throw err;
    var lines = data.split('\n');
    /*do something with */ lines[Math.floor(Math.random()*lines.length)];
 })
}
        