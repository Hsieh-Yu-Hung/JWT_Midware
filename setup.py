from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="jwt_auth_middleware",
    version="1.0.1",
    author="JWT Auth Team",
    author_email="support@jwt-auth.com",
    description="A comprehensive JWT Authentication Middleware for Flask Applications with MongoDB support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hsieh-Yu-Hung/JWT_Midware",
    project_urls={
        "Bug Reports": "https://github.com/Hsieh-Yu-Hung/JWT_Midware/issues",
        "Source": "https://github.com/Hsieh-Yu-Hung/JWT_Midware",
        "Documentation": "https://github.com/Hsieh-Yu-Hung/JWT_Midware#readme",
    },
    packages=find_packages(include=["jwt_auth_middleware", "jwt_auth_middleware.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
) 