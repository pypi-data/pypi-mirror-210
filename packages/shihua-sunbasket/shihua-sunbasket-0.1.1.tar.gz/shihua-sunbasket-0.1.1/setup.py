from setuptools import setup,find_packages

### 打开readme文件流，使用utf-8编码
with open("README.mdown","r",encoding="utf-8") as fh:
        long_description = fh.read()

setup(
        ### 包与作者信息
        name = 'shihua-sunbasket',
        version = '0.1.1',
        author = 'shihua',
        author_email = "15021408795@163.com",
        python_requires = ">=3.10.9",
        license = "MIT",

        ### 源码与依赖
        packages = find_packages(),
        include_package_data = True,
        description = ' Sunbasket is an embedded algorithmic auxiliary management tool that mainly provides five categories of information management, including algorithm, model, parameter, application, and data, model storage management, and algorithm logging. The main technologies use SQLite, ORM, and logging, and the design mode is factory mode.',
        # install_requires = ['sqlalchemy','pyyaml'],

        # ### 包接入点，命令行索引
        # entry_points = {
        #     'console_scripts': [
        #         'fichectl = fiche.cli:fiche'
        #     ]
        # }      

        ### pypi配置
        long_description = long_description,
        long_description_content_type = "text/markdown",
        url = "https://github.com/redblue0216/SunBasket",
        classsifiers = [
                "Programming Language :: Python :: 3.10",
                "License :: OSI Approved :: MIT License",
                "Topic :: Scientific/Engineering :: Artificial Intelligence"
        ] 
)