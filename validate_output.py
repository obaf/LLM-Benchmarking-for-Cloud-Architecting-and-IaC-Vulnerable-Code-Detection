import json
import hcl2

def get_assert(output, context):
    vars = context.get('vars', {})
    expected_ids_str = vars.get('expected_ids', '')
    expected_ids = [eid for eid in expected_ids_str.split(",") if eid.strip()]

    try:
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            output = output.split("```")[1].split("```")[0].strip()

        data = json.loads(output)
    except json.JSONDecodeError:
        return {"pass": False, "score": 0, "reason": "Output is not valid JSON"}

    predicted_ids = data.get("vulnerabilities", [])
    if not isinstance(predicted_ids, list):
        return {"pass": False, "score": 0, "reason": "'vulnerabilities' is not a list in JSON output."}

    # Relaxed Requirement: Require at least ONE matching Checkov ID, rather than ALL of them.
    found_expected = [eid for eid in expected_ids if eid in predicted_ids]
    
    if not found_expected:
        return {"pass": False, "score": 0, "reason": f"Failed to find ANY expected vulnerabilities. Expected: {expected_ids}. Found: {predicted_ids}"}

    # Calculate proportional score based on how many they found
    base_score = len(found_expected) / len(expected_ids)
    # Validate Remediation Code syntax
    rem_code = data.get("remediation_code", "")
    if not rem_code:
        return {"pass": True, "score": base_score * 0.5, "reason": f"Found valid IDs: {found_expected}, but no remediation_code provided"}

    try:
        if "```hcl" in rem_code:
           rem_code = rem_code.split("```hcl")[1].split("```")[0]
        elif "```terraform" in rem_code:
           rem_code = rem_code.split("```terraform")[1].split("```")[0]
        elif "```" in rem_code:
           rem_code = rem_code.split("```")[1].split("```")[0]

        parsed = hcl2.loads(rem_code)
    except Exception as e:
        return {"pass": True, "score": base_score * 0.5, "reason": f"Found valid IDs: {found_expected}, but invalid HCL syntax: {e}"}

    return {
        "pass": True,
        "score": base_score,
        "reason": f"Successfully identified {found_expected} and generated valid HCL remediation"
    }
