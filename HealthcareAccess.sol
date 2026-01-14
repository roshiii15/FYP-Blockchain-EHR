// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract HealthcareAccess {

    enum Role { NONE, DOCTOR, ADMIN, NURSE }

    struct Record {
        string cid;
        bool exists;
    }

    struct AuditLog {
        address user;
        string recordId;
        bool emergency;
        bool granted;
        Role role;
        uint256 timestamp;
    }

    address public owner;

    mapping(address => Role) public roles;
    mapping(string => Record) private records;
    mapping(address => AuditLog[]) private auditLogs;

    constructor() {
        owner = msg.sender;
    }

    /* ---------- ROLE MANAGEMENT ---------- */

    function assignRole(address user, Role role) external {
        require(msg.sender == owner, "Only owner");
        roles[user] = role;
    }

    /* ---------- STORE CID ONLY ---------- */

    function storeRecord(string memory recordId, string memory cid) external {
        require(msg.sender == owner, "Only owner");

        records[recordId] = Record(cid, true);
    }

    /* ---------- ACCESS CONTROL ---------- */

    function requestAccess(
        string memory recordId,
        bool emergency
    ) internal returns (bool) {

        require(records[recordId].exists, "Record not found");

        Role r = roles[msg.sender];
        bool allowed = false;

        if (r == Role.DOCTOR) {
            allowed = true;
        }
        else if (r == Role.ADMIN || r == Role.NURSE) {
            if (emergency == true) {
                allowed = true;
            }
        }

        auditLogs[msg.sender].push(
            AuditLog(
                msg.sender,
                recordId,
                emergency,
                allowed,
                r,
                block.timestamp
            )
        );

        return allowed;
    }

    /* ---------- GET CID ---------- */

    function getCID(
        string memory recordId,
        bool emergency
    ) external returns (string memory) {

        bool ok = requestAccess(recordId, emergency);
        require(ok, "Access denied");

        return records[recordId].cid;
    }

    /* ---------- AUDIT ---------- */

    function getMyAuditLogs() external view returns (AuditLog[] memory) {
        return auditLogs[msg.sender];
    }
}
