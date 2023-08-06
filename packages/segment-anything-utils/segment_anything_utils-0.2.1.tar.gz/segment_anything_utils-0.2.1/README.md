## 工具箱 for segment_anything

## 发布
先确保已经安装了最新版本的 setuptools, twine
```bash
pip install --user --upgrade setuptools twine
```
复制代码生成项目包：
```bash
python ./setup.py sdist
python -m twine upload dist/*
```