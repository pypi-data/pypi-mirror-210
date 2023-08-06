<a name="readme-top"></a>

# __Aksharify__

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
[![PyPI - Downloads][Downloads-shield]](https://pypistats.org/packages/aksharify)

<br />

<!-- ABOUT THE PROJECT -->
## About the module

The inspiration for this module came from a Numberphile video called "The Trinity Hall Prime," which I first saw in high school days. It motivated me to explore the possibilities of such a prime number. I created a Python module that uses a predetermined character set to turn photos into ASCII art. It manipulates images using the PIL package, transforming them to grayscale before mapping pixel values to ASCII letters. Users can change the character set to get different effects.

<!-- GETTING STARTED -->
## Getting Started

Before we begin, make sure you have one of recent versions of Python installed on your computer.

### Installation

```sh
python -m pip install aksharify
```

## Usage

```python
from aksharify import TextArt

# input image file
art = TextArt("Julia.png")

# see image
art.image.show()

# set dimension of output text
art.set_dim(80)

# genetate text
art.asciify()

# output into .txt file
art.text_output("output")

# generate colored text using html
art.colorify()

# output into .html file
art.color_output("output")
```

_For examples from user community, please refer to the [primepatel.github.io/aksharify](https://primepatel.github.io/aksharify)_


<!-- ROADMAP -->
## Roadmap

- [x] NumberiFy
- [-] Predifined order of characters
- [-] Getting images from URL
- [-] EmojiFy

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such a wonderful place to learn, be inspired, and create. Any contributions you make are `appreciated greatly`.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<!-- CONTACT -->
## Contact

Prime Patel - [@primepatel](https://twitter.com/primespatel) - primespatel@gmail.com

Project Link: [https://github.com/primepatel/aksharify](https://github.com/primepatel/aksharify)


<!-- ACKNOWLEDGMENTS -->
<!-- ## Acknowledgments

* []()
* []()
* []() -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/primepatel/Aksharify.svg?style=for-the-badge
[contributors-url]: https://github.com/primepatel/Aksharify/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/primepatel/Aksharify.svg?style=for-the-badge
[forks-url]: https://github.com/primepatel/Aksharify/network/members
[stars-shield]: https://img.shields.io/github/stars/primepatel/Aksharify.svg?style=for-the-badge
[stars-url]: https://github.com/primepatel/Aksharify/stargazers
[issues-shield]: https://img.shields.io/github/issues/primepatel/Aksharify.svg?style=for-the-badge
[issues-url]: https://github.com/primepatel/Aksharify/issues
[license-shield]: https://img.shields.io/github/license/primepatel/Aksharify.svg?style=for-the-badge
[license-url]: https://github.com/primepatel/Aksharify/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/primepatel
[Downloads-shield]: https://img.shields.io/pypi/dm/aksharify?style=for-the-badge