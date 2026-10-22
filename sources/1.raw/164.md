---
marp: false
theme: gaia
paginate: true

---

<style>
section {
    font-size: 175%;
}
</style>
---

# Chapter 9: Event Logging

## Secure Logging and Monitoring
### TCPRG4005 - Secure Programming

**Topics Covered:**
- Syslog and logging fundamentals
- Security event logging best practices  
- Centralized logging architecture
- OWASP logging guidelines
- Real-time monitoring and alerting

---

# Why Security Logging Matters

## Detection and Response

**When Prevention Fails:**
- Incident detection and response
- Forensic analysis after security events  
- Compliance and audit requirements
- Performance monitoring and debugging

**Cost of Poor Logging:**
- Equifax (2017): 76 days undetected
- Target (2013): 19 days of data theft
- Marriott (2018): 4 years unnoticed
- SolarWinds (2020): 9 months active

> **Key Point:** You can't defend against what you can't see. Most breaches remain undetected for months due to insufficient logging.

---

# Insufficient Logging & Monitoring

## OWASP Top 10 Security Risk

**Common Logging Failures:**
- Missing security-relevant events
- Poor log storage and protection
- Generic, uninformative messages
- No real-time monitoring or alerts
- Inadequate retention policies

**Critical Events to Log:**
- Authentication attempts (success/failure)
- Authorization decisions and failures
- Input validation failures
- Administrative actions
- Privilege escalations
- Data access patterns

> **Impact:** Most successful attacks remain undetected for months or years due to insufficient logging capabilities.

---

# How Attacks Go Undetected

## Typical Attack Timeline

**Week 1-2: Initial Compromise**
- ❌ No suspicious activity logging
- ❌ Missing process execution monitoring

**Month 1: Lateral Movement**
- ❌ No network traffic analysis
- ❌ Missing authentication anomaly detection

**Month 2-3: Privilege Escalation**
- ❌ No admin account monitoring
- ❌ Missing file system monitoring

**Month 3+: Data Exfiltration**
- ❌ No data access pattern analysis
- ❌ Missing baseline deviation alerts

**Average Detection Time: 287 days**
**Average Cost: $4.35 million per breach**

---

# Syslog: Foundation of System Logging

## Traditional Logging Infrastructure

**Syslog Architecture:**
```c
// Opening a syslog connection
openlog("authenticator", LOG_PID|LOG_PERROR, LOG_AUTH);

// Logging an event
syslog(LOG_NOTICE, "Login for '%s' failed", username);

// Closing connection
closelog();
```

**Syslog Severity Levels:**
- **EMERG (0):** System unusable
- **ALERT (1):** Action must be taken immediately
- **CRIT (2):** Critical conditions
- **ERR (3):** Error conditions
- **WARNING (4):** Warning conditions
- **NOTICE (5):** Normal but significant
- **INFO (6):** Informational messages
- **DEBUG (7):** Debug-level messages

**Modern Python Usage:**
```python
import syslog

syslog.openlog("webapp", syslog.LOG_PID, syslog.LOG_AUTH)
syslog.syslog(syslog.LOG_WARNING, f"Failed login for {username} from {ip}")
```

---

# Security Event Categories

## What to Log for Effective Monitoring

**Authentication Events:**
- Login success/failure
- Logout events  
- Account lockouts
- Password changes

**Authorization Events:**
- Access granted/denied
- Privilege escalations
- Permission changes
- Administrative actions

**System Events:**
- Configuration changes
- Service starts/stops
- System errors
- Performance issues

**Example Implementation:**
```python
import syslog

# Authentication logging
syslog.syslog(syslog.LOG_NOTICE, f"Login success: {username} from {ip}")
syslog.syslog(syslog.LOG_WARNING, f"Login failed: {username} from {ip}")

# Authorization logging  
syslog.syslog(syslog.LOG_INFO, f"Access granted: {user} to {resource}")
syslog.syslog(syslog.LOG_WARNING, f"Access denied: {user} to {resource}")
```

---

# Logging Strategy

## Best Practices for Security Logging

**What to Log:**
- All authentication events
- Authorization decisions
- Input validation failures
- Administrative actions
- System configuration changes

**What NOT to Log:**
- Passwords or credentials
- Personal information (PII)
- Credit card numbers
- Session tokens or API keys

**Centralized Logging:**
- Single point of analysis
- Tamper resistance
- Consistent formatting
- Automated processing
- Better security controls

**Log Review:**
- Regular monitoring required
- Real-time alerting for critical events
- Automated analysis where possible
- Human review for complex patterns

> **Remember:** Logs are incomplete by design - test what you log!

---

# Security Logging Best Practices

## Building Effective Security Monitoring

### **Comprehensive Logging Strategy:**

<div class="grid">

### **What to Log:**
- **All authentication** events
- **Authorization decisions** 
- **Input validation** failures
- **Privilege changes**
- **Configuration modifications**
- **Data access patterns**
- **Error conditions**
- **Performance anomalies**

### **What NOT to Log:**
- **Passwords** or credentials
- **Personal information** (PII)
- **Credit card numbers**
- **Social security numbers**
- **Private keys**
- **Session tokens**
- **API keys**

</div>

### **Log Message Design Principles:**

```python
# ✅ GOOD: Informative but safe
{
    "event": "login_failed",
    "user_id": "user123",
    "source_ip": "192.168.1.100",
    "reason": "invalid_password",
    "timestamp": "2024-07-26T10:30:15Z"
}

# ❌ BAD: Contains sensitive information
{
    "event": "login_failed", 
    "user_id": "user123",
    "password_attempted": "mypassword123",  # NEVER LOG THIS!
    "ssn": "123-45-6789",                   # NEVER LOG THIS!
    "credit_card": "4111111111111111"       # NEVER LOG THIS!
}
```

### **Time and Context Requirements:**
- **Synchronized time** across all systems (NTP)
- **Time zone awareness** (preferably UTC)
- **Unique transaction IDs** for correlation
- **Session identifiers** for user tracking
- **Request context** for web applications

> **Speaker Notes:** A good logging strategy balances comprehensive coverage with privacy protection. The goal is maximum security visibility with minimal privacy risk.

---

# Centralized Logging Architecture

## Securing Your Logs from Attackers

### **Why Centralize Logs?**

<div class="grid">

### **Security Benefits:**
- **Tamper resistance** - harder to modify
- **Persistent storage** - survives system compromise
- **Correlation capabilities** - cross-system analysis
- **Access control** - restricted log access
- **Backup and retention** - reliable preservation

### **Operational Benefits:**
- **Single point of analysis**
- **Consistent formatting**
- **Scalable storage**
- **Automated processing**
- **Cost efficiency**

</div>

### **Centralized Architecture Pattern:**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Web App   │    │   API App   │    │  Database   │
│             │    │             │    │             │
│   Logs ─────┼────┼─── Logs ────┼────┼─── Logs ────┼───┐
└─────────────┘    └─────────────┘    └─────────────┘   │
                                                         │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│   Firewall  │    │Load Balancer│    │   Server    │   │
│             │    │             │    │             │   │
│   Logs ─────┼────┼─── Logs ────┼────┼─── Logs ────┼───┤
└─────────────┘    └─────────────┘    └─────────────┘   │
                                                         │
                           ┌─────────────────────────────▼───┐
                           │     Centralized Log Server      │
                           │                                 │
                           │  ┌─────────┐  ┌─────────────┐  │
                           │  │ Storage │  │   Analysis  │  │
                           │  └─────────┘  └─────────────┘  │
                           │  ┌─────────┐  ┌─────────────┐  │
                           │  │ Alerts  │  │ Dashboards  │  │
                           │  └─────────┘  └─────────────┘  │
                           └─────────────────────────────────┘
```

### **Implementation Considerations:**
- **Network security** - encrypted transport (TLS)
- **Authentication** - verify log source identity
- **Storage security** - append-only, immutable logs
- **Access controls** - role-based log access
- **Retention policies** - compliance and storage management

> **Speaker Notes:** Centralized logging is crucial because compromised systems can't be trusted to maintain accurate logs. Attackers will try to cover their tracks by modifying local logs.

---

# Real-time Monitoring and Alerting

## Detecting Attacks as They Happen

### **Alert Categories and Response Times:**

<div class="three-column">

### **Critical (Immediate):**
- Active intrusion attempts
- Privilege escalation
- Data exfiltration
- System compromise
- **Response: < 15 minutes**

### **High (Fast):**
- Repeated login failures
- Suspicious user behavior
- Configuration changes
- Service disruptions
- **Response: < 1 hour**

### **Medium (Standard):**
- Policy violations
- Unusual access patterns
- Performance anomalies
- **Response: < 4 hours**

</div>

### **Smart Alerting Implementation:**

```python
class SecurityAlertManager:
    def __init__(self):
        self.alert_rules = {
            "brute_force": {
                "threshold": 5,
                "window": 300,  # 5 minutes
                "severity": "HIGH"
            },
            "privilege_escalation": {
                "threshold": 1,
                "window": 1,
                "severity": "CRITICAL"
            },
            "data_exfiltration": {
                "threshold": 1000,  # 1000 records
                "window": 3600,     # 1 hour
                "severity": "CRITICAL"
            }
        }
    
    def evaluate_event(self, event):
        for rule_name, rule in self.alert_rules.items():
            if self.matches_pattern(event, rule):
                self.trigger_alert(rule_name, event, rule["severity"])
    
    def trigger_alert(self, rule_name, event, severity):
        alert = {
            "alert_id": uuid.uuid4(),
            "rule": rule_name,
            "severity": severity,
            "event": event,
            "timestamp": datetime.utcnow(),
            "status": "NEW"
        }
        
        # Send to appropriate channels based on severity
        if severity == "CRITICAL":
            self.send_immediate_notification(alert)
        elif severity == "HIGH":
            self.send_priority_notification(alert)
        
        self.log_alert(alert)
```

> **Speaker Notes:** Real-time monitoring requires balancing speed with accuracy. Too many false positives will cause alert fatigue, while too few alerts might miss real attacks.

---

# OWASP AppSensor: Intelligent Attack Detection

## Beyond Traditional Logging

### **What is AppSensor?**

OWASP AppSensor is a **conceptual framework** for:
- **Real-time attack detection** within applications
- **Automated response** to suspicious behavior
- **Self-defending applications** that can adapt to threats

### **AppSensor Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Detection Points        │  Response Actions                │
│  ├─ Input Validation     │  ├─ Log Event                   │
│  ├─ Authentication       │  ├─ Block Request               │
│  ├─ Session Management   │  ├─ Lock Account                │
│  ├─- Access Control      │  ├─ Increase Monitoring         │
│  └─ Data Layer          │  └─ Disable Functionality       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 AppSensor Engine                            │
│  ├─ Event Correlation                                       │
│  ├─ Threshold Management                                    │
│  ├─ Attack Detection                                        │
│  └─ Response Coordination                                   │
└─────────────────────────────────────────────────────────────┘
```

### **Detection Point Categories:**

<div class="grid">

### **Input Validation:**
- IE1: Unexpected HTTP command
- IE2: Attempt to invoke unsupported function
- IE3: Force browsing attempt
- IE4: Disallowed HTTP method

### **Authentication:**
- AE1: Multiple failed passwords
- AE2: Multiple failed usernames  
- AE3: High rate of login attempts
- AE4: Unexpected logout patterns

</div>

> **Speaker Notes:** AppSensor represents the evolution from passive logging to active defense. Applications become self-aware and can respond to attacks in real-time.

---

# AppSensor Detection Points in Detail

## Comprehensive Attack Pattern Recognition

### **Request Exception (RE) Detection Points:**

```python
class AppSensorDetector:
    def detect_re1_unexpected_http_command(self, request):
        """RE1: Request includes unexpected HTTP command"""
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE']
        if request.method not in allowed_methods:
            return self.create_detection_event('RE1', request)
    
    def detect_re2_attempt_to_access_file(self, request):
        """RE2: Attempt to access common web application file"""
        suspicious_files = ['/admin', '/config', '/.env', '/backup']
        if any(file in request.path for file in suspicious_files):
            return self.create_detection_event('RE2', request)
    
    def detect_re3_force_browsing(self, request):
        """RE3: Force browsing attempt"""
        if self.is_forced_browsing(request.path, request.user):
            return self.create_detection_event('RE3', request)
```

### **Input Validation (IE) Detection Points:**

```python
def detect_ie1_cross_site_scripting(self, input_data):
    """IE1: Cross Site Scripting Attack"""
    xss_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
    if any(pattern in input_data.lower() for pattern in xss_patterns):
        return self.create_detection_event('IE1', input_data)

def detect_ie2_sql_injection(self, input_data):
    """IE2: SQL Injection Attack"""
    sql_patterns = ["'", '"', '--', ';', 'UNION', 'SELECT', 'DROP']
    if any(pattern.upper() in input_data.upper() for pattern in sql_patterns):
        return self.create_detection_event('IE2', input_data)
```

### **Session Management (SE) Detection Points:**

```python
def detect_se1_modifying_session_token(self, request):
    """SE1: Modifying existing cookie"""
    if self.session_token_modified_externally(request):
        return self.create_detection_event('SE1', request)

def detect_se2_adding_session_token(self, request):
    """SE2: Adding new cookie"""
    if self.unexpected_cookie_added(request):
        return self.create_detection_event('SE2', request)
```

> **Speaker Notes:** AppSensor's strength lies in its comprehensive catalog of detection points. Each point represents a specific attack pattern that applications can monitor for in real-time.

---

# AppSensor Response Actions

## Automated Defense Mechanisms

### **Response Action Categories:**

<div class="grid">

### **Passive Responses:**
- **ASR-A:** Log the event only
- **ASR-B:** Log the event and alert admin
- **ASR-C:** Log the event and alert user

### **Active Responses:**
- **ASR-D:** Block the specific request
- **ASR-E:** Block the user account
- **ASR-F:** Block the source IP address

</div>

### **Advanced Responses:**
- **ASR-G:** Execute a process or script
- **ASR-H:** Redirect user to different page
- **ASR-I:** Generate fake server response
- **ASR-J:** Forward request to honeypot

### **Implementation Example:**

```python
class AppSensorResponseManager:
    def __init__(self):
        self.response_rules = {
            'IE1': ['ASR-A', 'ASR-D'],  # XSS: Log and block request
            'IE2': ['ASR-A', 'ASR-D', 'ASR-E'],  # SQLi: Log, block, lock account
            'AE1': ['ASR-A'],  # Failed password: Log only
            'AE2': ['ASR-A', 'ASR-F'],  # Multiple failures: Log and block IP
        }
    
    def execute_response(self, detection_point, event_data):
        """Execute appropriate response actions"""
        responses = self.response_rules.get(detection_point, ['ASR-A'])
        
        for response in responses:
            if response == 'ASR-A':
                self.log_security_event(detection_point, event_data)
            elif response == 'ASR-D':
                self.block_request(event_data['request_id'])
            elif response == 'ASR-E':
                self.lock_user_account(event_data['user_id'])
            elif response == 'ASR-F':
                self.block_ip_address(event_data['source_ip'])
    
    def log_security_event(self, detection_point, event_data):
        """Log the security event with full context"""
        security_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "detection_point": detection_point,
            "severity": self.get_severity(detection_point),
            "user_id": event_data.get('user_id'),
            "source_ip": event_data.get('source_ip'),
            "user_agent": event_data.get('user_agent'),
            "request_data": event_data.get('request_data'),
            "response_actions": self.response_rules[detection_point]
        }
        
        logger.warning(f"AppSensor Detection: {json.dumps(security_event)}")
```

> **Speaker Notes:** AppSensor's response actions create a graduated response system. The application can escalate from passive monitoring to active blocking based on the severity and frequency of attacks.

---

# Log Retention and Compliance

## Legal and Regulatory Requirements

### **Industry-Specific Requirements:**

<div class="three-column">

### **Financial Services:**
- **SOX:** 7 years
- **PCI DSS:** 1 year minimum
- **GLBA:** Varies by record type
- **Basel III:** 5-10 years

### **Healthcare:**
- **HIPAA:** 6 years minimum
- **FDA:** 2-10 years
- **Clinical trials:** 15+ years

### **Government:**
- **FISMA:** 6 years
- **FedRAMP:** 90 days online
- **NIST:** Risk-based

</div>

### **Log Retention Strategy:**

```python
class LogRetentionManager:
    def __init__(self):
        self.retention_policies = {
            "security_events": {
                "hot_storage": 90,    # days - immediate access
                "warm_storage": 365,  # days - quick retrieval  
                "cold_storage": 2555, # days - 7 years archive
                "compliance": "SOX, PCI-DSS"
            },
            "audit_logs": {
                "hot_storage": 30,
                "warm_storage": 180,
                "cold_storage": 2555,
                "compliance": "SOX"
            },
            "access_logs": {
                "hot_storage": 30,
                "warm_storage": 90,
                "cold_storage": 365,
                "compliance": "Internal policy"
            }
        }
    
    def archive_logs(self, log_type, age_days):
        """Move logs to appropriate storage tier"""
        policy = self.retention_policies[log_type]
        
        if age_days > policy["cold_storage"]:
            return self.delete_logs(log_type, age_days)
        elif age_days > policy["warm_storage"]:
            return self.move_to_cold_storage(log_type, age_days)
        elif age_days > policy["hot_storage"]:
            return self.move_to_warm_storage(log_type, age_days)
```

### **Storage Considerations:**
- **Encryption at rest** for sensitive logs
- **Compression** for long-term storage
- **Indexing** for searchability
- **Backup and recovery** procedures
- **Geographic distribution** for disaster recovery

> **Speaker Notes:** Compliance isn't just about meeting legal requirements - it's about ensuring you have the data needed for incident response and forensic analysis when breaches occur.

---

# Performance and Scalability

## Managing High-Volume Security Logging

### **The Logging Performance Challenge:**

<div class="grid">

### **Volume Challenges:**
- **High-traffic sites:** 10,000+ events/second
- **Enterprise environments:** Millions of events/day
- **Security events:** 5-15% of total log volume
- **Storage growth:** 50-100GB per day typical

### **Performance Impact:**
- **Application latency** from logging overhead
- **Network bandwidth** for log transmission
- **Storage I/O** bottlenecks
- **Processing delays** for real-time analysis

</div>

### **Optimization Strategies:**

```python
# Asynchronous logging to prevent blocking
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

class HighPerformanceSecurityLogger:
    def __init__(self, buffer_size=1000, flush_interval=5):
        self.buffer = []
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def log_security_event(self, event):
        """Non-blocking security event logging"""
        self.buffer.append(event)
        
        if len(self.buffer) >= self.buffer_size:
            await self.flush_buffer()
    
    async def flush_buffer(self):
        """Flush buffer to persistent storage"""
        if not self.buffer:
            return
            
        batch = self.buffer.copy()
        self.buffer.clear()
        
        # Process batch asynchronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, self.write_batch, batch)
    
    def write_batch(self, events):
        """Write events to storage (runs in thread)"""
        try:
            # Bulk write to reduce I/O overhead
            for event in events:
                # Write to centralized log system
                self.send_to_log_server(event)
        except Exception as e:
            # Fallback to local logging
            local_logger.error(f"Failed to send logs: {e}")
```

### **Sampling and Filtering:**
- **Statistical sampling** for high-volume events
- **Priority-based filtering** for critical events
- **Rate limiting** for noisy sources
- **Intelligent deduplication** for repeated events

> **Speaker Notes:** High-performance logging requires careful engineering to avoid becoming a bottleneck. The goal is comprehensive security visibility without impacting application performance.

---

# Security Information and Event Management (SIEM)

## Centralizing Security Intelligence

### **SIEM Architecture and Capabilities:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SIEM Platform                            │
├─────────────────────────────────────────────────────────────┤
│  Data Collection     │  Processing Engine                   │
│  ├─ Log Aggregation  │  ├─ Normalization                   │
│  ├─ Agent Collection │  ├─ Correlation Rules               │
│  ├─ API Integration  │  ├─ Pattern Matching                │
│  └─ Network Capture  │  └─ Machine Learning                │
├─────────────────────────────────────────────────────────────┤
│  Analytics & Detection │  Response & Management             │
│  ├─ Behavior Analysis   │  ├─ Incident Management          │
│  ├─ Threat Intelligence │  ├─ Automated Response           │
│  ├─ Risk Scoring        │  ├─ Forensic Analysis            │
│  └─ Anomaly Detection   │  └─ Compliance Reporting         │
└─────────────────────────────────────────────────────────────┘
```

### **SIEM Integration Example:**

```python
class SIEMIntegration:
    def __init__(self, siem_endpoint, api_key):
        self.siem_endpoint = siem_endpoint
        self.api_key = api_key
        
    def send_security_event(self, event):
        """Send structured event to SIEM"""
        siem_event = {
            "source": "webapp",
            "timestamp": event["timestamp"],
            "event_type": event["event_type"],
            "severity": self.map_severity(event["severity"]),
            "user_id": event.get("user_id"),
            "source_ip": event.get("source_ip"),
            "details": event.get("details", {}),
            "raw_log": json.dumps(event)
        }
        
        try:
            response = requests.post(
                f"{self.siem_endpoint}/events",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=siem_event,
                timeout=5
            )
            
            if response.status_code != 200:
                self.handle_siem_error(response, siem_event)
                
        except requests.RequestException as e:
            # Fallback to local logging if SIEM unavailable
            local_logger.error(f"SIEM unavailable: {e}")
            self.log_locally(siem_event)
```

### **Popular SIEM Solutions:**
- **Commercial:** Splunk, IBM QRadar, ArcSight, LogRhythm
- **Open Source:** ELK Stack, OSSIM, Wazuh, Graylog
- **Cloud:** AWS Security Hub, Azure Sentinel, Google Chronicle

> **Speaker Notes:** SIEM systems provide the intelligence layer on top of raw logging. They can correlate events across multiple systems to detect complex, multi-stage attacks that individual systems might miss.

---

# Threat Hunting with Logs

## Proactive Security Analysis

### **Threat Hunting Methodology:**

<div class="grid">

### **Hypothesis-Driven Hunting:**
1. **Form hypothesis** about potential threats
2. **Design queries** to test hypothesis
3. **Analyze results** for indicators
4. **Investigate anomalies** found
5. **Document findings** and improve detection

### **Common Hunting Scenarios:**
- **Lateral movement** detection
- **Data exfiltration** patterns
- **Privilege escalation** attempts
- **Persistence mechanisms**
- **Command and control** communications

</div>

### **Log Analysis Queries for Threat Hunting:**

```sql
-- Hunt for potential lateral movement
SELECT 
    user_id, 
    source_ip, 
    COUNT(DISTINCT target_system) as systems_accessed,
    MIN(timestamp) as first_access,
    MAX(timestamp) as last_access
FROM authentication_logs 
WHERE timestamp > NOW() - INTERVAL 24 HOUR
    AND event_type = 'login_success'
GROUP BY user_id, source_ip
HAVING systems_accessed > 5
ORDER BY systems_accessed DESC;

-- Hunt for data exfiltration patterns
SELECT 
    user_id,
    source_ip,
    SUM(data_size) as total_downloaded,
    COUNT(*) as download_events,
    MAX(timestamp) as last_download
FROM data_access_logs
WHERE timestamp > NOW() - INTERVAL 7 DAY
    AND action = 'download'
GROUP BY user_id, source_ip
HAVING total_downloaded > 1000000000  -- 1GB threshold
ORDER BY total_downloaded DESC;

-- Hunt for unusual administrative activity
SELECT 
    admin_user,
    action_type,
    COUNT(*) as action_count,
    STRING_AGG(DISTINCT target_user, ', ') as affected_users
FROM admin_action_logs
WHERE timestamp > NOW() - INTERVAL 24 HOUR
    AND action_type IN ('user_created', 'permission_granted', 'password_reset')
GROUP BY admin_user, action_type
HAVING action_count > 10
ORDER BY action_count DESC;
```

### **Automated Threat Hunting:**

```python
class ThreatHunter:
    def __init__(self, log_database):
        self.db = log_database
        self.hunting_rules = self.load_hunting_rules()
    
    def hunt_lateral_movement(self, time_window_hours=24):
        """Hunt for lateral movement patterns"""
        query = """
        SELECT user_id, source_ip, COUNT(DISTINCT target_host) as host_count
        FROM network_logs 
        WHERE timestamp > NOW() - INTERVAL %s HOUR
        GROUP BY user_id, source_ip
        HAVING host_count > 5
        """
        
        results = self.db.execute(query, [time_window_hours])
        
        for result in results:
            if result['host_count'] > 10:
                self.create_hunting_alert(
                    "POTENTIAL_LATERAL_MOVEMENT",
                    f"User {result['user_id']} accessed {result['host_count']} systems",
                    result
                )
```

> **Speaker Notes:** Threat hunting transforms logs from reactive incident response tools into proactive threat detection capabilities. It requires security analysts to think like attackers and look for subtle indicators of compromise.

---

# Practical Exercise: Implementing Security Logging

## Building a Complete Logging Solution

### **Exercise Requirements:**

Your task is to implement a comprehensive security logging system for a web application with these components:

1. **Structured Security Logger** with event categorization
2. **Real-time Alert System** with configurable thresholds
3. **Log Retention Manager** with compliance features
4. **SIEM Integration** capability
5. **Basic Threat Hunting** queries

### **Starter Code Framework:**

```python
class SecurityLoggingFramework:
    def __init__(self, config):
        self.config = config
        self.logger = self.setup_logger()
        self.alert_manager = AlertManager(config['alerts'])
        self.retention_manager = RetentionManager(config['retention'])
        self.siem_integration = SIEMIntegration(config['siem'])
    
    def log_authentication_event(self, event_type, user_id, ip_address, **kwargs):
        """Log authentication-related events"""
        # TODO: Implement structured authentication logging
        pass
    
    def log_authorization_event(self, event_type, user_id, resource, action, **kwargs):
        """Log authorization-related events"""
        # TODO: Implement structured authorization logging
        pass
    
    def log_data_access_event(self, user_id, resource, action, data_size=None, **kwargs):
        """Log data access events"""
        # TODO: Implement structured data access logging
        pass
    
    def evaluate_security_alerts(self, event):
        """Evaluate if event triggers any security alerts"""
        # TODO: Implement alert evaluation logic
        pass
```

### **Implementation Challenges:**
- **Performance optimization** for high-volume logging
- **Alert tuning** to minimize false positives
- **Compliance mapping** for your industry
- **Integration testing** with monitoring tools

> **Speaker Notes:** This exercise brings together all the concepts covered in the chapter. Students should focus on building a production-ready system that balances comprehensive coverage with practical performance requirements.

---

# Log Analysis Tools and Techniques

## Extracting Security Intelligence from Logs

### **Essential Log Analysis Tools:**

<div class="three-column">

### **Command Line:**
- **grep/awk/sed** - Pattern matching
- **jq** - JSON processing
- **cut/sort/uniq** - Data manipulation
- **tail/head** - File navigation

### **Visualization:**
- **Kibana** - ELK stack dashboard
- **Grafana** - Metrics and logs
- **Splunk** - Enterprise search
- **Tableau** - Business intelligence

### **Programming:**
- **Python/Pandas** - Data analysis
- **R** - Statistical analysis
- **SQL** - Database queries
- **Jupyter** - Interactive analysis

</div>

### **Log Analysis Patterns:**

```bash
# Find failed login attempts from specific IP
grep "authentication.*failed" security.log | grep "192.168.1.100" | wc -l

# Extract unique user agents from access logs
cat access.log | jq -r '.user_agent' | sort | uniq -c | sort -nr

# Analyze login patterns by hour
cat security.log | jq -r 'select(.event_type=="login") | .timestamp' | 
  cut -c12-13 | sort | uniq -c

# Find privilege escalation events
grep -E "(sudo|su|admin|root)" security.log | 
  jq 'select(.severity=="HIGH" or .severity=="CRITICAL")'
```

### **Statistical Analysis for Anomaly Detection:**

```python
import pandas as pd
import numpy as np
from scipy import stats

class LogAnomalyDetector:
    def __init__(self, baseline_days=30):
        self.baseline_days = baseline_days
        
    def detect_login_anomalies(self, login_events):
        """Detect unusual login patterns"""
        df = pd.DataFrame(login_events)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        # Analyze hourly login patterns
        hourly_counts = df.groupby(['user_id', 'hour']).size().reset_index(name='count')
        
        # Calculate z-scores for each user's hourly patterns
        user_stats = hourly_counts.groupby('user_id')['count'].agg(['mean', 'std'])
        
        anomalies = []
        for _, row in hourly_counts.iterrows():
            user_mean = user_stats.loc[row['user_id'], 'mean']
            user_std = user_stats.loc[row['user_id'], 'std']
            
            if user_std > 0:
                z_score = (row['count'] - user_mean) / user_std
                if abs(z_score) > 3:  # 3-sigma rule
                    anomalies.append({
                        'user_id': row['user_id'],
                        'hour': row['hour'],
                        'count': row['count'],
                        'z_score': z_score,
                        'anomaly_type': 'unusual_login_time'
                    })
        
        return anomalies
```

> **Speaker Notes:** Effective log analysis requires both automated tools and human expertise. The goal is to surface meaningful patterns and anomalies from vast amounts of log data.

---

# Common Logging Anti-Patterns

## What Not to Do

### **Anti-Pattern 1: Logging Everything**

```python
# ❌ BAD: Excessive logging
def process_request(request):
    logger.info(f"Processing request: {request}")
    logger.debug(f"Request headers: {request.headers}")
    logger.debug(f"Request body: {request.body}")
    logger.info(f"User agent: {request.headers.get('User-Agent')}")
    logger.info(f"IP address: {request.remote_addr}")
    
    result = business_logic(request)
    
    logger.info(f"Business logic result: {result}")
    logger.debug(f"Database queries executed: {db.query_count}")
    logger.info(f"Response time: {time.time() - start_time}")
    
    return result

# ✅ GOOD: Selective, meaningful logging
def process_request(request):
    start_time = time.time()
    
    # Log only security-relevant events
    if is_sensitive_operation(request):
        security_logger.info({
            "event": "sensitive_operation",
            "user_id": request.user.id,
            "operation": request.path,
            "source_ip": request.remote_addr
        })
    
    result = business_logic(request)
    
    # Log performance issues
    response_time = time.time() - start_time
    if response_time > 2.0:
        performance_logger.warning({
            "event": "slow_response",
            "endpoint": request.path,
            "response_time": response_time
        })
    
    return result
```

### **Anti-Pattern 2: Inconsistent Log Formats**

```python
# ❌ BAD: Inconsistent formats
logger.info("User john logged in from 192.168.1.1")
logger.warning("Failed login: user=jane, ip=10.0.0.1, reason=bad password")
logger.error("Authentication error for user 'bob' (IP: 172.16.0.1): invalid token")

# ✅ GOOD: Consistent structured format
def log_auth_event(event_type, user_id, ip_address, **kwargs):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": "authentication",
        "event_type": event_type,
        "user_id": user_id,
        "source_ip": ip_address,
        **kwargs
    }
    auth_logger.info(json.dumps(event))

log_auth_event("login_success", "john", "192.168.1.1")
log_auth_event("login_failed", "jane", "10.0.0.1", reason="invalid_password")
log_auth_event("auth_error", "bob", "172.16.0.1", error="invalid_token")
```

### **Anti-Pattern 3: No Log Monitoring**

```python
# ❌ BAD: Write logs and forget
logger.error("Database connection failed")
logger.warning("High memory usage detected")
logger.critical("Security breach detected")

# ✅ GOOD: Logs with actionable monitoring
class MonitoredLogger:
    def __init__(self):
        self.alert_thresholds = {
            "database_errors": {"count": 5, "window": 300},
            "memory_warnings": {"count": 3, "window": 600},
            "security_events": {"count": 1, "window": 1}
        }
    
    def error(self, message, category=None):
        logger.error(message)
        
        if category and category in self.alert_thresholds:
            self.check_alert_threshold(category, message)
    
    def check_alert_threshold(self, category, message):
        # Check if threshold exceeded and trigger alerts
        if self.threshold_exceeded(category):
            self.send_alert(category, message)
```

> **Speaker Notes:** These anti-patterns are extremely common and can make logging systems ineffective or even counterproductive. Good logging discipline is as important as good coding discipline.

---

# Questions for Discussion

## Critical Thinking About Security Logging

### **Scenario-Based Questions:**

1. **E-commerce Platform:** Your online store is experiencing a surge in failed login attempts. How would you distinguish between a brute force attack and legitimate users forgetting passwords during a promotion?

2. **Healthcare System:** Patient records are being accessed at unusual hours. How do you log and monitor this without violating patient privacy?

3. **Financial Services:** Suspicious trading patterns are detected in your logs. What information should be logged, and how quickly should alerts be triggered?

4. **Cloud Migration:** You're moving from on-premises to cloud infrastructure. How does this change your logging strategy and compliance requirements?

### **Design Challenges:**

- How would you design logging for a **microservices architecture** with 50+ services?
- What's the balance between **comprehensive logging** and **storage costs**?
- How do you handle logging in **high-availability systems** that can't tolerate downtime?
- What logging strategy would you use for **IoT devices** with limited resources?

### **Compliance Scenarios:**

- Your company operates in both **EU (GDPR)** and **US (SOX)** - how do you design a unified logging strategy?
- A **security incident** occurs and lawyers want to preserve all logs - what's your process?
- **Audit requirements** change and now require 10 years of retention - how do you adapt?

### **Take-Home Project:**
Design and implement a security logging system for a web application of your choice. Include:
- Structured event logging
- Real-time alerting rules
- Compliance-aware retention
- SIEM integration capability
- Basic threat hunting queries

> **Speaker Notes:** These discussion questions help students think about the practical challenges of implementing security logging in real-world environments with competing requirements and constraints.

---

# Chapter 9 Summary

## Security Logging Essentials

**Core Principles:**
- Log all security-relevant events
- Use centralized logging systems
- Protect logs from tampering
- Review logs regularly
- Plan retention and compliance

**Key Events to Log:**
- Authentication (success/failure)
- Authorization decisions
- Administrative actions
- System configuration changes
- Input validation failures

**Best Practices:**
- Never log sensitive data (passwords, PII)
- Use structured, consistent formats
- Implement real-time monitoring
- Test your logging implementation
- Maintain appropriate retention policies

> **Remember:** "You can't defend what you can't see"

**Next:** Chapter 10 - Architecture and Design Patterns
