# Async Quick Reference for LangGraph

## 🚀 Quick Patterns

### Database Operations

```python
# ✅ Pattern: asyncio.to_thread() for Google Sheets API
async def save_to_database(self, data):
    result = await asyncio.to_thread(
        self._service.worksheets['TableName'].insert_rows,
        [data], value_input_option='RAW'
    )
    return result
```

### API Calls

```python
# ✅ Pattern: Gmail API async wrapper
async def get_emails(self, query):
    messages = await asyncio.to_thread(
        self._gmail_service.users().messages().list,
        userId='me', q=query
    )
    return await asyncio.to_thread(messages.execute)
```

### Authentication

```python
# ✅ Pattern: OAuth refresh async
async def refresh_credentials(self):
    if self._credentials.expired:
        await asyncio.to_thread(self._credentials.refresh, Request())
    return await asyncio.to_thread(build, 'gmail', 'v1', credentials=self._credentials)
```

## 🔍 Quick Detection

### Find Blocking Calls

```bash
# Search for blocking patterns
grep -r "\.execute()" src/ --include="*.py"
grep -r "requests\." src/ --include="*.py"
grep -r "\.refresh(" src/ --include="*.py"

# Test for blocking at runtime
langgraph dev  # Should start without --allow-blocking
```

### Common Error Messages

- `Blocking call to socket.socket.connect` → Wrap API call with asyncio.to_thread()
- `coroutine 'X' was never awaited` → Add `await` keyword
- `RuntimeWarning: coroutine was never awaited` → Check async/await usage
- `asyncio.run() cannot be called from a running event loop` → Use thread-based async init

### FastAPI Event Loop Compatibility

```python
# ✅ Module-level async initialization (FastAPI compatible)
try:
    loop = asyncio.get_running_loop()
    # In event loop - use thread-based async
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.submit(run_in_new_thread).result(timeout=30)
except RuntimeError:
    # No event loop - use asyncio.run()
    result = asyncio.run(async_function())
```

## ⚡ Quick Migration Steps

1. **Identify**: Search for `.execute()`, `requests.`, `.refresh()` calls
2. **Wrap**: Use `await asyncio.to_thread(blocking_function, *args)`
3. **Update signature**: Add `async def` to method
4. **Add await**: Ensure all callers use `await`
5. **Test**: Run `langgraph dev` without `--allow-blocking`

## 🚨 Quick Checklist

- [ ] All database calls use `asyncio.to_thread()`
- [ ] All API calls use `asyncio.to_thread()`
- [ ] All async methods have `async def`
- [ ] All async calls have `await`
- [ ] Server starts without `--allow-blocking`
- [ ] No "Blocking call" errors in logs

## 📚 Full Guide

See `ASYNC_PROGRAMMING_LANGGRAPH_GUIDE.md` for comprehensive patterns and examples.
