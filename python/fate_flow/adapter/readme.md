这个目录为了适配不同类型的DAG SCHEMA用的；
提交上来的dag_schema中包含了`dag`,`kind`,`schema_version`，其中的kind就是用来表示dag的种类，
根据dag的种类，../adapter 下找到对应的适配器去控制job的提交；
目录结构有一定要求：
- adapter: 适配器根目录
    - bfia: 以协议名称命名的目录
        - bridge: 固定名称，表示桥接，这个模块下面要实现JobController类，即本协议的作业控制器类