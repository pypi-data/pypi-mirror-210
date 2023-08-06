# 关于FreeplanIr的简单介绍 
    用于解析freeplan脑图的*.mm文件，输出为从根节点到子节点的数据
    
    例如你的脑图 a-b-c
                  -d-e
                  -f-g
                h-i-g
                 -k-l
        那么最终的输出为[
            [a, b, c],
            [a, d, e],
            [a, f, g],
            [h, i, j],
            [h, k, l]
        ]
## 使用方法
    安装相关模块后
    导入模块和类
    file_path = r"XXXX.mm" # 你的文件路径
    test_plan = FreeplanIr(file_path) # 实例化类
    datas = test_plan.plan_test() # 调用plan_test方法即可
    print(datas)  
  此方法返回的结果就是如上所说，需要注意次方返回目前仅支持所有节点的长度一致。
  