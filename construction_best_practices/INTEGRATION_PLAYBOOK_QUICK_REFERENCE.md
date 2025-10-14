# 🔗 Integration Playbook Quick Reference

**Use this card for rapid integration workflow execution.**

## 📋 Before You Start (Definition of Ready)

- [ ] **Objective & success metrics** written
- [ ] **Versions & environments** chosen
- [ ] **Auth method** decided + secrets path created
- [ ] **Data model & state transitions** sketched
- [ ] **Test matrix** drafted
- [ ] **Context-gap log** created with 3+ top unknowns

## ⚡ 11-Step Quick Process

| Step   | Activity              | Artifact                         | Time    |
| ------ | --------------------- | -------------------------------- | ------- |
| **1**  | Scope & objectives    | `00-scope.md`                    | 30-60m  |
| **2**  | Context gap mapping   | `context-gaps.md`                | Ongoing |
| **3**  | Architecture & state  | `diagrams/state-and-sequence.md` | 2-4h    |
| **4**  | Auth & safety         | `config.example.yaml`            | 1-2h    |
| **5**  | Test strategy         | `tests/test_*.py`                | 4-8h    |
| **6**  | Spike implementation  | `src/client.py`                  | 4-8h    |
| **7**  | Robustness hardening  | Enhanced implementation          | 2-4h    |
| **8**  | Documentation         | `README.md`                      | 2-3h    |
| **9**  | Runbook               | `RUNBOOK.md`                     | 2-3h    |
| **10** | Compliance & security | Security review                  | 1-2h    |
| **11** | Rollout plan          | Feature flags + monitoring       | 2-4h    |

## 🧪 Test Categories (Required)

```bash
# Contract tests - Schema validation
pytest integrations/<service>/ -m contract

# Semantic tests - Cause→effect behaviors
pytest integrations/<service>/ -m "integration and semantic"

# Resilience tests - Error handling
pytest integrations/<service>/ -m resilience

# Performance tests - Load and timing
pytest integrations/<service>/ -m performance
```

## 📁 File Structure Template

```
integrations/<service>/
├── 00-scope.md                 # Objectives & constraints
├── context-gaps.md              # Investigation log
├── README.md                    # Quickstart guide
├── RUNBOOK.md                   # Operations guide
├── config.example.yaml          # Configuration template
├── diagrams/state-and-sequence.md
├── src/
│   ├── client.py               # Integration client
│   ├── models.py               # Domain models
│   └── constants.py            # Business constants
└── tests/
    ├── test_contract.py        # Schema validation
    ├── test_semantics.py       # Stateful behavior
    ├── test_resilience.py      # Error handling
    └── test_performance.py     # Load testing
```

## 🚨 Critical Success Patterns

### ✅ DO This

- **Test semantic contracts**: POST → GET state consistency
- **Use real services**: Development TDD with actual API calls
- **Implement idempotency**: Same key = same result
- **Plan for failures**: Rate limits, timeouts, partial failures
- **Document operations**: Runbook with troubleshooting
- **Feature flags**: Off-by-default with gradual rollout

### ❌ DON'T Do This

- Skip semantic contract testing (only test happy path)
- Hardcode secrets in code
- Ignore rate limits and retry logic
- Deploy without monitoring
- Skip rollback planning

## 🎯 Definition of Done Checklist

- [ ] **Context gaps closed** or documented
- [ ] **Integration tests green** (contract + semantic + resilience)
- [ ] **Proof run recorded** with sanitized traces
- [ ] **README complete** with troubleshooting
- [ ] **Runbook complete** with rollback plan
- [ ] **Feature flag configured** for gradual rollout

## ⚡ Emergency Commands

```bash
# Create integration issue
gh issue create --template integration.yml

# Test integration quickly
pytest integrations/<service>/ -m "contract or semantic" -v

# Check integration health
curl -s https://api.service.com/health || echo "Service down"

# Disable integration (emergency)
kubectl set env deployment/app SERVICE_ENABLED=false
```

## 📊 Quality Gates

| Metric            | Threshold | Purpose                |
| ----------------- | --------- | ---------------------- |
| **Test Coverage** | ≥95%      | Comprehensive testing  |
| **Error Rate**    | <1%       | Production reliability |
| **P95 Latency**   | <5s       | User experience        |
| **Documentation** | 100%      | Operational readiness  |

## 🔄 Daily Execution Loop

1. **Pull top context gap** → run targeted probe
2. **Update context-gaps.md** with findings
3. **Add/adjust tests** to codify understanding
4. **Keep spike vertical** (resist scope creep)
5. **Commit frequently** with evidence

## 📞 Getting Help

- **Playbook Guide**: `construction_best_practices/INTEGRATION_PLAYBOOK_GUIDE.md`
- **Issue Template**: `.github/ISSUE_TEMPLATE/integration.yml`
- **Examples**: `integrations/_template/` directory
- **Team Channel**: #integrations on Slack

---

**🔗 Print this card and keep it handy during integration work. Every external service integration should follow this proven process for production reliability.**
