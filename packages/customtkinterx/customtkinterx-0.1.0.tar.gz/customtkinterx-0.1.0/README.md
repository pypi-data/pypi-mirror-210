# CustomTkinterX
`customtkinter`的扩展组件功能库

## Fluent主题
尚未完善设置，修改了`CTk` `CTkToplevel` `CTkFrame` `CTkButton` `CTKEntry` `CTkComboBox`等类。
```python
from customtkinter import *
from customtkinterx import *

CTkFluentTheme()
```

## 自定义窗口
原窗口因标题栏与边框的限制，导致界面效果极差，但是仍可以通过一些方法自定义窗口`wm_overrideredirect`。
平台支持`Windows` `MacOS` `Linux`，其中界面效果支持最好的是`Windows`，`MacOS` `Linux`无法使用透明色，完全消除边框使用圆角，
及将图标保留至任务栏，采用置顶的方法保持窗口的显示。

### 基础示例
```python
from customtkinter import *
from customtkinterx import *

root = CTkCustom()

root.mainloop()
```

### 添加缩放窗口大小的手柄
```python
CTKCustom.create_sizegrip()
```
```python
from customtkinter import *
from customtkinterx import *

root = CTkCustom()
root.create_sizegrip()

root.mainloop()
```