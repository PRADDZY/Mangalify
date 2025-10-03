from daytona import daytona, DaytonaConfig
  
# Define the configuration
config = DaytonaConfig(api_key="dtn_2c2092a5039864bccdb72d1da43508d829c4a6f4d9cdc62605afc87c526e1892")

# Initialize the Daytona client
daytona = daytona(config)

# Create the Sandbox instance
sandbox = daytona.create()

# Run the code securely inside the Sandbox
response = sandbox.process.code_run('print("Hello World from code!")')
if response.exit_code != 0:
  print(f"Error: {response.exit_code} {response.result}")
else:
    print(response.result)
  