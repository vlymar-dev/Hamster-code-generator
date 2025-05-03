# Proxy Setup

**Hamster Keys Generator** uses proxies to bypass geographical restrictions and rate limits for game API requests.

## Configuration
1. Create or edit `proxies.txt` in the project root.
2. Add proxy servers in the format:
    ```sh
    http://username:password@ip:port
    http://ip:port
    socks5://username:password@ip:port
    ```

## Example `.proxies.txt`
```
http://proxy1:pass@192.168.1.1:8080
socks5://proxy2:pass@192.168.1.2:1080
```

## Testing Proxies
Run the keygen to verify proxy connectivity:
```sh
python main.py  # With STARTUP_METHOD=1
```

Check logs in `var/logs` for proxy-related errors.
