pipeline {

    agent any

    environment {

        PYTHON_EXE = 'C:\\Users\\umram\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'

        EC2_HOST = '13.206.204.208'

        DOCKER_IMAGE = 'umramahejabeen/invoice-tracker'

        DOCKER_CREDENTIALS = 'dockerhub-creds'

        EC2_CREDENTIALS = 'ec2-ssh-key'

        CONTAINER_NAME = 'invoice-tracker'

        APP_PORT = '5000'
    }


    stages {

        // =========================================================
        // CHECK PYTHON
        // =========================================================

        stage('Check Python') {

            steps {

                echo '========================================'
                echo 'CHECK PYTHON'
                echo '========================================'

                bat '''
                    "%PYTHON_EXE%" --version
                '''
            }
        }


        // =========================================================
        // CREATE VIRTUAL ENVIRONMENT
        // =========================================================

        stage('Create Virtual Environment') {

            steps {

                echo '========================================'
                echo 'CREATE VIRTUAL ENVIRONMENT'
                echo '========================================'

                bat '''
                    if not exist venv (
                        "%PYTHON_EXE%" -m venv venv
                    )

                    venv\\Scripts\\python.exe --version
                '''
            }
        }


        // =========================================================
        // INSTALL DEPENDENCIES
        // =========================================================

        stage('Install Dependencies') {

            steps {

                echo '========================================'
                echo 'INSTALL PYTHON DEPENDENCIES'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m pip install --upgrade pip

                    venv\\Scripts\\python.exe -m pip install -r requirements.txt

                    if exist requirements-dev.txt (
                        venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
                    )
                '''
            }
        }


        // =========================================================
        // LINT
        // =========================================================

        stage('Lint') {

            steps {

                echo '========================================'
                echo 'RUN PYTHON LINT'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m flake8 app tests --max-line-length=120
                '''
            }
        }


        // =========================================================
        // TEST
        // =========================================================

        stage('Test') {

            steps {

                echo '========================================'
                echo 'RUN PYTHON TESTS'
                echo '========================================'

                bat '''
                    venv\\Scripts\\python.exe -m pytest tests -v
                '''
            }
        }


        // =========================================================
        // PREPARE EC2
        // =========================================================

        stage('Prepare EC2') {

            steps {

                echo '========================================'
                echo 'TEST EC2 SSH CONNECTION'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        echo Copying Jenkins SSH key...

                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"


                        echo Fixing SSH key permissions...

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /inheritance:r

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /grant:r "SYSTEM:(R)"

                        icacls "%WORKSPACE%\\jenkins-ec2-key.pem" /grant:r "Administrators:(R)"


                        echo Testing SSH connection...

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -o ConnectTimeout=30 ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker --version"
                    '''
                }
            }
        }


        // =========================================================
        // CLONE PROJECT ON EC2
        // =========================================================

        stage('Clone Project on EC2') {

            steps {

                echo '========================================'
                echo 'CLONE PROJECT ON EC2'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "rm -rf ~/invoice-tracker && git clone https://github.com/Umramahejabeen/invoice-tracker.git ~/invoice-tracker"
                    '''
                }
            }
        }


        // =========================================================
        // DOCKER HUB LOGIN
        // =========================================================

        stage('Docker Hub Login') {

            steps {

                echo '========================================'
                echo 'DOCKER HUB LOGIN ON EC2'
                echo '========================================'

                withCredentials([

                    usernamePassword(

                        credentialsId: "${DOCKER_CREDENTIALS}",

                        usernameVariable: 'DOCKER_USERNAME',

                        passwordVariable: 'DOCKER_PASSWORD'
                    ),

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        echo Logging in to Docker Hub on EC2...

                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        powershell -NoProfile -Command "$env:DOCKER_PASSWORD | ssh -o StrictHostKeyChecking=no -i \\"$env:WORKSPACE\\jenkins-ec2-key.pem\\" \\"$env:SSH_USER@$env:EC2_HOST\\" 'docker login --username $env:DOCKER_USERNAME --password-stdin'"

                        if errorlevel 1 (
                            echo Docker Hub login failed
                            exit /b 1
                        )

                        echo Docker Hub Login Successful
                    '''
                }
            }
        }


        // =========================================================
        // BUILD DOCKER IMAGE
        // =========================================================

        stage('Build Docker Image') {

            steps {

                echo '========================================'
                echo 'BUILD DOCKER IMAGE'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "cd ~/invoice-tracker && docker build -t %DOCKER_IMAGE%:latest ."
                    '''
                }
            }
        }


        // =========================================================
        // PUSH DOCKER IMAGE
        // =========================================================

        stage('Push Docker Image') {

            steps {

                echo '========================================'
                echo 'PUSH DOCKER IMAGE'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker push %DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }


        // =========================================================
        // RUN CONTAINER
        // =========================================================

        stage('Run Container') {

            steps {

                echo '========================================'
                echo 'DEPLOY DOCKER CONTAINER'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker rm -f %CONTAINER_NAME% 2>/dev/null || true && docker pull %DOCKER_IMAGE%:latest && docker run -d --restart unless-stopped --name %CONTAINER_NAME% -p %APP_PORT%:%APP_PORT% %DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }


        // =========================================================
        // CHECK CONTAINER
        // =========================================================

        stage('Check Container') {

            steps {

                echo '========================================'
                echo 'CHECK DOCKER CONTAINER'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "docker ps --filter name=%CONTAINER_NAME%"
                    '''
                }
            }
        }


        // =========================================================
        // HEALTH CHECK
        // =========================================================

        stage('Health Check') {

            steps {

                echo '========================================'
                echo 'APPLICATION HEALTH CHECK'
                echo '========================================'

                withCredentials([

                    sshUserPrivateKey(

                        credentialsId: "${EC2_CREDENTIALS}",

                        keyFileVariable: 'SSH_KEY',

                        usernameVariable: 'SSH_USER'
                    )

                ]) {

                    bat '''
                        copy /Y "%SSH_KEY%" "%WORKSPACE%\\jenkins-ec2-key.pem"

                        ssh ^
                        -o StrictHostKeyChecking=no ^
                        -i "%WORKSPACE%\\jenkins-ec2-key.pem" ^
                        %SSH_USER%@%EC2_HOST% ^
                        "sleep 10 && curl --fail http://localhost:%APP_PORT%/ || (docker logs %CONTAINER_NAME% && exit 1)"
                    '''
                }
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================

    post {

        success {

            echo '========================================'

            echo 'PIPELINE SUCCESSFUL'

            echo 'Invoice Tracker deployed successfully'

            echo '========================================'
        }


        failure {

            echo '========================================'

            echo 'PIPELINE FAILED'

            echo 'Check Jenkins Console Output'

            echo '========================================'
        }


        always {

            echo 'Invoice Tracker Jenkins Pipeline finished.'

            bat '''
                if exist "%WORKSPACE%\\jenkins-ec2-key.pem" (
                    del /F /Q "%WORKSPACE%\\jenkins-ec2-key.pem"
                )
            '''
        }
    }
}