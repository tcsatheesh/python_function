Run in command line

    func init --docker --language python --worker-runtime python --source-control
    func new --language python --name StorageTrigger
    
    func new --language python --name StorageTrigger --template "Azure Blob Storage Trigger"

    docker build --tag <docker id>/azurefunctionsimage:v1.0.0 .

    docker run -p 8080:80 -it <docker id>/azurefunctionsimage:v1.0.0
