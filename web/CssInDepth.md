# CssInDepth 学习记录

## 优先级

有几个地方注意：

1. 自定义即作者的样式， 继承的样式， 浏览器默认样式

2. 自定义样式中， 内联样式高于选择器样式， 或者看那个样式出现得晚， 或者离元素最近

3. 自定义样式可针对id, class, tag进行声明， 优先级依次递减，且相同级别个数多的胜出。如 1,0,0表示选择器为一个id，则优先级高于0,2,0(表示没有id，但有2个class)

## 相对单位

绝对单位如px，mm，cm， in等应该尽量避免使用

作者非常推荐使用，针对响应式现代不同尺寸的屏幕

### em

1em means the font size of the current element（注意当前元素！！！）; 对于大多数浏览器， 默认的字体尺寸为16px

```css
.padded {
  font-size: 16px;
  padding: 1em;
}
```

em有时会有一些奇怪的行为， 多半是由于其基于当前元素的字体尺寸造成的， 所以我们更常使用rem

### rem

rem是相对于root元素的， 无论在文档何处使用， 1.5rem都有相同的尺寸！

Does this mean you should use rems everywhere and abandon the other options? No. In CSS, again, the answer is often, “it depends.”（看情况） Rems are but one tool in your toolbag. An important part of mastering CSS is learning when to use which tool.

My default is to use rems for font sizes, pixels for borders, and ems for most other measures, especially paddings, margins, and border radius (though I favor the use of percentages for container widths when necessary)

