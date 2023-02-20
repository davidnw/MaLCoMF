# MaLCoMF
Modular LLM Converstation Management Framework
## Overview
This is a set of microservices for managing a converstation with a LLM.
An LLM prompt is assembled by asking each microservice to provide their element of the agent conversing with the LLM.  For example a 'personality' may add the 'I am a...' part of the prompt, or a 'constitution' may add the 'please avoid using sexist language in your reply' part of the prompt.
The aim is to allow each microservice to decide what is best to provide at a particular point in a conversation.

## Basic structure philosophy
I have tried to make this as flexible as posible for implementation utilising various LLMs and message brokers, however initially the framework is based on RabbitMQ and GPT3.5.
Overall MaLCoMF is based on an Event Driven Architecture

## Early Version
Early itterations are experimental.  The initial test cradle for the microservices will utilise multi-threading in a python app rather than individual processes.
