# CssInDepth 学习记录

## 工具

学会浏览器的控制台工具F12进行css的分析

## 优先级

有几个地方注意：

1. 自定义即作者的样式， 继承的样式， 浏览器默认样式
2. 自定义样式中， 内联样式高于选择器样式， 或者看那个样式出现得晚， 或者离元素最近
3. 自定义样式可针对id, class, tag进行声明， 优先级依次递减，且相同级别个数多的胜出。如 1,0,0表示选择器为一个id，则优先级高于0,2,0(表示没有id，但有2个class)
4. 少用!important/内联样式/id, 多用class来指定样式

## 相对单位

> 绝对单位如px，mm，cm， in等应该尽量避免使用

作者非常推荐使用相对单位，针对响应式现代不同尺寸的屏幕

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

My default is

* rems for font sizes
* pixels for borders
* ems for most other measures, especially paddings, margins, and border radius (though I favor the use of percentages for container widths when necessary)

### 不要使用pixel

除了一些绝对必要的时候, 如设置一条一个pixel宽度的线条等

### 相对于viewport的单位

所谓viewport即视口, 就是屏幕中浏览器显示内容的窗口(仅限内容部分)

* vh, viewport高度的1/100
* vw, viewport宽度的1/100
* vmin, viewport高度和宽度中小的那个的1/100(比如在横屏时一般是高度小, 竖屏时一般是宽度小)
* vmax, viewport高度和宽度中大的那个的1/100(比如在横屏时一般是宽度大, 竖屏时一般是高度大)

有时也采用如下的组合方式保证基本的字体大小

```css
html {
  font-size: calc(0.5em + 1vw);
}
```

## box模型

缺省的, 一个元素被看作一个box, 其宽度为left margin--left border--left padding--content--right padding--right border--right margin

高度同理.

### box-sizing

而且, 设置该元素的高度和宽度是指其内容content的, 而非整个box的, 也即属性是:`box-sizing: content-box`

我们可以设置`box-sizing: border-box`, 此时的高度或宽度就扩展到包括border了

建议对于页面上的所有元素及其伪类做如下设置:

```css
:root {
 box-sizing: border-box;
}

*, ::before, ::after {
 box-sizing: inherit;
}
```

另外建议以以下的方式设置列之间的距离:

```css
.someclass {
  float: left;
  width: calc(30% - 1.5em);
  margin-left: 1.5em;
}
```

> 对于元素的高度, 一般不建议进行设置, 无论是绝对还是相对高度(包括使用百分比). 文档被设计成有一个限制的宽度及无限的高度, 高度通常由其内容来决定. 当的确需要设置高度时, 你需要处理overflow溢出

> 某些场景下, 如果希望某容器铺满整个屏幕, 请使用100vh, 即视口的全高

### overflow

针对溢出的内容有4种处理:

* visible, 默认的, 即溢出的内容也可见
* hideden, 不可见
* scroll, 无论是否溢出, 都给出滚动条(不推荐使用)
* auto, 发生溢出时出现滚动条

同时, 溢出也可分为xy两个方向即: `overflow-x, overflow-y`

box模型典型与float布局结合. 如果需要的是等高的列则显得有些吃力, 此时我们可以使用表格布局来减少麻烦

## CSS table布局

简单的设置容器为`display: table`, 各列为`display: table-cell`即可得到很好的布局. 还可以使用`border-spacing: 1.5em 0;`来设置各列间距

但现在是flexbox布局又出现了

## flexbox柔性/弹性布局

简单的将容器设置成`display: flex`即可, 然后各子元素可以随意的设置width/margin等, 该**FlexBox**将自动进行处理, 且各子元素有相同的高度

另外, 使用flex进行布局时同样不推荐明确设置子元素的具体高度. 可考虑使用`min-height: 3em;`或`max-height: 3em`等

## 内容垂直居中

这一直是css中的一个问题

实际上`vertical-align: middle`样式申明将只对`inline and table-cell`元素有效

以下是一些方法汇总:

* Can you use a natural height container? Apply an equal top and bottom padding to the container to center its contents.
* Do you need a specific height container, or do you need to avoid using padding? Use display: `table-cell` and `vertical-align: middle` on your container.
* Can you use flexbox? If you don’t need to support IE9, you can center your content with flexbox. See chapter 5.
* Is the inner content only one line of text? Set a tall line height equal to the desired container height. This will force the container to row to contain the line height. If the contents aren’t inline, you may have to set them to `inline-block`.
* Do you know the height of both the container and the inner content? Center the contents with absolute positioning. See chapter 7. (I only recommend this when all approaches mentioned here fail.)
* What if you don't know the height of the inner element? Use absolute positioning in conjunction with a transform. See chapter 15 for an example. (Again, I only recommend this if you've ruled out all other options.)

> <http://howtocenterincss.com/> 是一个帮你布局的好地方!

## margin为负值

border不能为负值显而易见, 同时padding也不可以(意味着内容不能越过border).

但margin可以为负值, 意味着元素可以向四个方向进行扩展, 或者说与周围的元素进行了重叠!

> 一般不考虑这种使用, 因为移出容器意味着可能失去控制. 

---

## 理解页面布局layout

目前, 把图片移到边上并让文本环绕只能使用`float: left/right`, 再者就是兼容性问题, 除此外可以不予考虑. 请使用新的`flexbox`和`grid`进行布局

## flex

将一个元素设置成`display: flex`则就把它变成了一个`flex container`, 其子元素即为``flex item`

> By default, flex items align side by side, left to right, all in one row. The flex container fills the available width like a block element, but the flex items may not necessarily fill the width of their flex container.
>The flex items are all the same height, determined naturally by their contents.

> The items are placed along a line called the main axis, which goes from the main-start (left) to the main-end (right).
> Perpendicular(垂直) to the main axis is the cross axis. This goes from the cross-start (top) to the cross-end (bottom).

注意这些概念: **flex container, flex items, and the two axes**

## grid

现代Web布局方案, 二维结构