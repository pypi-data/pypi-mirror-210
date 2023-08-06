import traceback
import matplotlib.pyplot as pyplot
import numpy


def __pre(title,info_dic):
    pyplot.rcParams['font.family'] = 'SimHei'
    pyplot.rcParams['axes.unicode_minus']=False
    pyplot.rcParams['figure.figsize'] = (8,3)
    pyplot.title(title)
    #pyplot.style.use('dark_background') 
    colors = pyplot.get_cmap('YlGnBu')(numpy.linspace(0.2,0.7,len(info_dic)))
    color  = '#37ACC3'
    return colors,color




def out_bar_chart(title,info_dic:dict,out_path):
    '''
    柱形图
    info_dic = {'a1':100,'b2':200,'c3':300,'d4':900}
    show_tool.out_bar_chart(info_dic,'test.png')
    '''
    x_label_list = list(info_dic.keys())
    x = numpy.arange(len(x_label_list))
    y = numpy.array(list(info_dic.values()))
    colors,color = __pre(title,info_dic)
    pyplot.bar(x, y, tick_label=x_label_list, width=0.3,color=color)
    pyplot.savefig(out_path)
    pyplot.clf()
    #pyplot.show()

    

def out_cake_chart(title,info_dic:dict,out_path):
    '''
    饼图
    表现的是数据的比例
    info_dic = {'a1':100,'b2':200,'c3':300,'d4':900}
    show_tool.out_bar_chart(info_dic,'test.png')
    '''

    labels = list(info_dic.keys())
    x = numpy.array(list(info_dic.values()))
    colors,color = __pre(title,info_dic)
    # 数值，标签，顺时针，偏转90度，颜色
    pyplot.pie(x=x, labels=labels, counterclock=False, startangle=90, colors=colors)
    pyplot.savefig(out_path)
    pyplot.clf()
    #pyplot.show()



def out_line_chart(title,info_dic:dict,out_path):
    '''
    折线图
    表现的是数据变化情况
    info_dic = {'a1':100,'b2':200,'c3':300,'d4':900}
    show_tool.out_line_chart(info_dic,'test.png')
    '''
    
    labels = list(info_dic.keys())
    x = numpy.array(list(info_dic.values()))
    colors,color = __pre(title,info_dic)
    pyplot.plot(labels, x, color=color)
    pyplot.savefig(out_path)
    pyplot.clf()
    #pyplot.show()

def out_histogram(title,info_dic:dict,out_path):
    '''
    直方图
    表现的是数据的分布情况,各有多少个
    info_dic = {'a1':100,'b2':200,'c3':300,'d4':900}
    show_tool.out_line_chart(info_dic,'test.png')
    '''
    labels = list(info_dic.keys())
    x = numpy.array(list(info_dic.values()))
    colors,color = __pre(title,info_dic)
    pyplot.hist(x, color=color)
    pyplot.savefig(out_path)
    pyplot.clf()
    #pyplot.show()

def out_scatter_diagram_2D(title,info_dic:dict,out_path):
    '''
    二维散点图
    info_dic = {'a1':(100,100),'b2':(200,200),'c3':(300,300),'d4':(900,900)}
    '''
    labels = list(info_dic.keys())
    info   = list(info_dic.values())
    x_list = []
    y_list = []
    for key in info_dic:
        try:
            x_list.append(info_dic[key][0])
            y_list.append(info_dic[key][1])
            
        except Exception:
            traceback.print_exc()
            print('[Error]:out_scatter_diagram_2D,parms index error。' , key , info_dic)
            return
    x = numpy.array(x_list)
    y = numpy.array(y_list)

    colors,color = __pre(title,info_dic)
    pyplot.scatter(x, y)
    pyplot.savefig(out_path)
    pyplot.clf()
    #pyplot.show()


def out_scatter_diagram_3D(title,info_dic:dict,out_path):
    '''
    三维散点图
    info_dic = {'a1':(100,100,100),'b2':(200,200,200),'c3':(300,300,300),'d4':(900,900,900)}
    '''
    labels = list(info_dic.keys())
    info   = list(info_dic.values())
    x_list = []
    y_list = []
    z_list = []
    for key in info_dic:
        try:
            x_list.append(info_dic[key][0])
            y_list.append(info_dic[key][1])
            z_list.append(info_dic[key][2])
        except Exception:
            traceback.print_exc()
            print('[Error]:out_scatter_diagram_3D,parms index error。' , key , info_dic)
            return
    x = numpy.array(x_list)
    y = numpy.array(y_list)
    z = numpy.array(z_list)
    colors,color = __pre(title,info_dic)
    ax3d = pyplot.subplot(projection = '3d')

    ax3d.scatter(x , y , z ,c = color)
    pyplot.savefig(out_path)
    pyplot.clf()
    #pyplot.show()




