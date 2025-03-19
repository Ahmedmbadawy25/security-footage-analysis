# Footfall Analysis Dashboard
This dashboard was created to serve as an analytical dashboard serving this [`repository`](https://github.com/Ahmedmbadawy25/footfall-dashboard-analysis) which given a camera stream, counts visitors and writes to a database the details of the user visits. This dashboard then reads this data and provides analytical insights based on the data gathered from the camera.

<div align='center'>
<img width="600" alt="Screenshot 2025-03-19 at 5 30 38 pm" src="https://github.com/user-attachments/assets/d7a2b4d4-35ed-4c62-ab61-898e85fb0f6d" />
<img width="600" alt="Screenshot 2025-03-19 at 5 31 21 pm" src="https://github.com/user-attachments/assets/ad42fbe8-d8e0-42a8-96ec-caf14b265849" />
<img width="600" alt="Screenshot 2025-03-19 at 5 31 37 pm" src="https://github.com/user-attachments/assets/81741770-9186-4381-b153-1d5dfe46f957" />
</div>

To build and deploy a local copy follow these simple steps.

## Documentation

<table>
<tbody>
  <tr>
    <td><b>Stacks used</b></td>
    <td>
        <a href="https://github.com/facebook/react" target="_blank"><img alt="React" src="https://shields.io/badge/react-black?logo=react&style=for-the-badge"></a>
        <a href="https://github.com/expressjs/express" target="_blank"><img alt="Express" src="https://img.shields.io/badge/Express.js-000000?logo=express&logoColor=fff&style=flat"></a>
        <a href="https://github.com/nodejs/node" target="_blank"><img alt="Node" src="https://img.shields.io/badge/node.js-339933?style=for-the-badge&logo=Node.js&logoColor=white"></a>
        <a href="https://github.com/mongodb/mongo" target="_blank"><img alt="MongoDB" src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white"></a>
    </td>
  </tr>
  <tr>
    <td><b>Dependency managers</b></td>
    <td>
  <a href="https://github.com/nodejs/node" target="_blank"><img alt="Node" src="https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white"></a>
    </td>
  </tr>
  <tr>
    <td><b>Code style</b></td>
    <td>
  <a href="https://github.com/topics/javascript" target="_blank"><img alt="JavaScript" src="https://shields.io/badge/JavaScript-F7DF1E?logo=JavaScript&logoColor=000&style=flat-square"></a>
  <a href="https://github.com/tailwindlabs/tailwindcss" target="_blank"><img alt="TailwindCSS" src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white"></a>
  </tr>
</tbody>
</table>

Follow the following step-by-step to obtain and run the project. First follow the requirements to install all requirements to setup the environment for the project on your machine. Then build the project, through the build steps.

### Requirements

* **`git`**: To obtain a copy of this code, you can clone it using [Git](https://git-scm.com/). Make sure to download the correct version for your Operating System.
```sh
git clone https://github.com/Ahmedmbadawy25/footfall-dashboard-analysis.git
```

* **`Node`**: The application uses npm to install dependencies, which needs [`NodeJS`](https://nodejs.org/en). Make sure to download the correct version for your Operating System.


* **`npm`**: The application uses MERN Stack (React, Node, Express, MongoDB) and therefore dependencies can be handled using [`npm`](https://www.npmjs.com/). Make sure to download the correct version for your Operating System.
* Open two terminal windows and in the first terminal run the following command ```cd backend```.
* In the second terminal run the following command ```cd frontend```.
* Then in both terminals run the following command:
```sh
npm install  # Downloads all packages and dependices required to run and build the project
```

### Build steps

* Open a new terminal window, run the following command to build the project.
```sh
npm run build  # Builds the project
```

### Run steps
* Create a .env file in the backend folder where you will add all the secret keys required for the proper funcitoning of the backend. It should look something like this:

```sh
PORT = 8000
MONGODB_URI = mongodb+srv://testuser:123@cluster.123.mongodb.net/collection?retryWrites=true&w=majority
JWT_SECRET = my-secret-key
JWT_EXPIRES_IN = 1h
```
* Your backend is now setup and you can run your application.

* Open a new terminal window, run the following command to change your directory to the backend ```cd backend```.
* Then run the following command to run the backend of the project. The application should be running on `http://127.0.0.1:8000/`. 
```sh
npm run dev  # Runs the server of the project
```
> NOTE: You can open this link `http://127.0.0.1:8000/` in your browser to verify the backend is running.

* Now to run the frontend, open a new terminal window
* Run this command ```cd frontend``` to navigate to the frontend directory
* Run the following command to run the frontned:
```sh
npm run start  # Runs the frontend of the project
```
* Your appliction should now be running. If not automatically redirected, enter the following link into your browser ```http://localhost:3000```

## License
This project is not licensed under any open-source license. All rights are reserved by the author. The project is only available for educational purposes.

## Contact
For any queries, please contact the author at [a.badawyam@gmail.com](mailto:a.badawyam@gmail.com) or [badawy.am@gmail.com](mailto:badawy.am@gmail.com).
