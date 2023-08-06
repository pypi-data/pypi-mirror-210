# pyqt设置生成器
一个可以根据`json schema`自动生成设置界面的工具

![](example/image.png)

功能:
- 错误提示
- 选项描述
- 默认值提示

拓展语法`item_list`:
你可以通过指定 `item_list` 来限定内容
例如:
``` json
"optional": {
    "type": "string",
    "title": "test2",
    "item_list": ["bule", "green", "yellow"]
}
```
效果:
![](example/img2.png)