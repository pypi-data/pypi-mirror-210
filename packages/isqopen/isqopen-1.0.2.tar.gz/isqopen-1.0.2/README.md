# isq-qcis python cor



isQ为对接中科院量子信息与量子科技创新研究院超导量子硬件，定制化开发了一个简化版的编译器isQ-core，并提供了离线的python包isqopen，详情请参考[isQ-core帮助文档](http://www.arclightquantum.com/isq-core/)

isQ编译器也提供了编译到该硬件的选项`--target qcis`。由于硬件目前还不支持反馈控制，因此在使用isQ编写该硬件线路时，不能将测量结果赋值存入int变量，否则会报错，如

```c++
qbit q[3];
procedure main(){
    ...
    int a = M(q[0]); // 报错
}
```


当isQ编译成功后，会得到`.qcis`文件，用户可通过[isqopen](http://www.arclightquantum.com/isq-core/#_5)离线提交任务

