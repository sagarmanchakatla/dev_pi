# ADR 001: Use FastAPI as the Web Framework

## Status
Accepted

## Date
2026-06-12

## Context
We need a Python web framework for the Platform API.

## Decision
Use FastAPI.

## Reasons
- Automatic OpenAPI documentation
- Native async support
- Pydantic validation built in
- Strong performance

## Consequences
- Team must understand async Python
- Requires Python 3.8+
