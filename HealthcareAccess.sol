// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract HealthcareAccess {

    struct Record {
        string cid;
        bool exists;
    }

    struct AuditLog {
        address user;
        string recordId;
        bool emergency;
        bool granted;
        string role;
        uint256 timestamp;
    }

    address public owner;

    mapping(string => Record) private records;
    mapping(address => AuditLog[]) private auditLogs;

    constructor() {
        owner = msg.sender;
    }

    /* ---------- STORE CID ONLY ---------- */

    function storeRecord(string memory recordId, string memory cid) external {
        require(msg.sender == owner, "Only owner can store records");

        records[recordId] = Record(cid, true);
    }

    /* ---------- ACCESS CONTROL ---------- */
    /*
        Role comes from FRONTEND (doctor / nurse / admin)
        Emergency also comes from frontend toggle
    */
    function requestAccess(
        string memory recordId,
        string memory role,
        bool emergency
    ) internal returns (bool) {

        require(records[recordId].exists, "Record not found");

        bool allowed = false;

        // Doctor: always allowed
        if (keccak256(bytes(role)) == keccak256(bytes("doctor"))) {
            allowed = true;
        }
        // Nurse / Admin: only emergency
        else if (
            keccak256(bytes(role)) == keccak256(bytes("nurse")) ||
            keccak256(bytes(role)) == keccak256(bytes("admin"))
        ) {
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
                role,
                block.timestamp
            )
        );

        return allowed;
    }

    /* ---------- GET CID WITH ACCESS CHECK ---------- */

    function getCID(
        string memory recordId,
        string memory role,
        bool emergency
    ) external returns (string memory) {

        bool ok = requestAccess(recordId, role, emergency);
        require(ok, "Access denied");

        return records[recordId].cid;
    }

    // ADD THIS BELOW getCID()

    function getCIDView(string memory recordId)
        external
        view
        returns (string memory)
    {
        require(records[recordId].exists, "Record not found");
        return records[recordId].cid;
    }


    /* ---------- AUDIT ---------- */

    function getMyAuditLogs() external view returns (AuditLog[] memory) {
        return auditLogs[msg.sender];
    }
}
