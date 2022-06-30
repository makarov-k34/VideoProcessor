#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

requirements = [
    'face_recognition',
    'joblib',
    'requests',
    'opencv-python'
]

setup(
    name='video_processor',
    version='1.0.0',
    description="Early face recognition from any source(videofile stream image batch) ",
    author="Makarov Konstantin",
    author_email='',
    url='',
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='video_processor',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]

)
