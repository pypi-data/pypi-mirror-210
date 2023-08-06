

from setuptools import find_packages, setup
name = 'nonebot_plugin_smart_reply'

setup(
    name=name,  
    version='0.0.33',
    author="Special-Week",
    author_email='2385612749@qq.com',
    description="encapsulate logger",
    python_requires=">=3.8.1",
    packages=find_packages(),
    long_description="reply插件",
    url="https://github.com/Special-Week/nonebot_plugin_smart_reply",

    package_data={name: ['resource/json/*', 'resource/audio/*']},

    # 设置依赖包
    install_requires=["EdgeGPT","revChatGPT","httpx","loguru","pillow","nonebot2","nonebot-adapter-onebot"],
)
