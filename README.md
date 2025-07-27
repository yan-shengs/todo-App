# 基于flask + vue的记事web后端

## Background



作为一个web全栈新手入门再适合不过
涉及简单的前端身份验证(jwt),增删改查,密码加盐,orm数据库操作,mvc结构等



## Usage

### （一）项目中有uv.lock文件

如果克隆的项目中已经存在`uv.lock`文件，这意味着项目的依赖已经被锁定好了。你只需要执行下面的命令，就能快速同步依赖，让项目在你的环境中顺利运行：

```bash
uv sync
```

### （二）项目中只有pyproject.toml文件

要是项目中只有`pyproject.toml`文件，而没有`uv.lock`文件，那你需要先锁定依赖，再进行同步。具体操作如下：

```bash
uv lock
uv sync
```

### （三）启动项目

```bash
uv run main.py
```



## Front

### (todo-App-front)[https://github.com/yan-shengs/todo-App-front]
