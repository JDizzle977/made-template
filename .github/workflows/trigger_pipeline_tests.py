name: CI Tests

on:
  push:
    branches:
      - main
    paths:
      - project/**

    workflow_dispatch:
    
jobs:
  test:
    runs-on: ubuntu-latest

    steps: 
      - name: Check out Code 
        uses: actions/checkout@v4

      - name: Make File executable
        run: |
              chmod +x project/tests.sh 

      - name: Run Tests
        run: project/tests.sh 
