<br />
<p align="center">
  <a href="https://github.com/recreationx/oneBus">
    <img src="static/images/favicon.ico" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">oneBus</h3>

  <p align="center">
    a bus stop toolkit for singapore
    <br />
    <a href="https://github.com/recreationx/oneBus"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://one-bus.herokuapp.com/">View Demo</a>
    ·
    <a href="https://github.com/recreationx/oneBus/issues">Report Bug</a>
    ·
    <a href="https://github.com/recreationx/oneBus/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project
The main focus of this project is to provide a easy-to-use tool to find info about buses in Singapore.

### Built With
* Bootstrap
* JQuery
* Flask

## Getting Started
The project is built in Python 3.9.2, but is more likely compatitable with older Python 3 versions. 

### Prerequisites

1. Clone the repo
  ```sh
  git clone https://github.com/recreationx/oneBus.git
  ```

2. It is recommend to run this within a virtual environment so as to not affect existing Python installations.
  ```sh
  virtualenv env
  ```
  and activate the new virtual environment.

3. Install required packages
  ```sh
  pip install -r requirements.txt
  ```

4. A Google Maps JS API key is provided in `templates/bustable.html` for demo purposes. using your own is recommended.

5. Run project
  ```sh
  python main.py
  ```

## Usage

Usage is intuitive. Check out the demo to try out. 

## Roadmap

See the [open issues](https://github.com/recreationx/oneBus/issues) for a list of proposed features (and known issues).\

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

NIL
