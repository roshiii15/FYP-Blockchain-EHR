// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EHRRegistry {

    struct Record {
        string recordId;   // file name or patient ID
        string cid;        // IPFS CID of encrypted EHR
    }

    mapping(string => Record) private records;

    event RecordStored(string indexed recordId, string cid);

    // Store a CID with its associated recordId (file or patient identifier)
    function storeRecord(string memory recordId, string memory cid) public {
        records[recordId] = Record(recordId, cid);
        emit RecordStored(recordId, cid);
    }

    // Retrieve stored record
    function getRecord(string memory recordId) public view returns (string memory, string memory) {
        Record memory r = records[recordId];
        return (r.recordId, r.cid);
    }
}
