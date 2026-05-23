// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract AgentRegistry {
    address public owner;

    struct Agent {
        string  agentId;
        address wallet;
        uint256 tradesExecuted;
        uint256 feesEarned;      // in USDT0 units (6 decimals)
        uint256 registeredAt;
        bool    active;
    }

    mapping(address => Agent) public agents;
    mapping(string => address) public agentIdToAddress;
    address[] public agentList;

    event AgentRegistered(address indexed wallet, string agentId, uint256 timestamp);
    event TradeRecorded(address indexed wallet, string agentId, uint256 totalTrades, uint256 feesEarned);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerAgent(string calldata agentId, address wallet) external onlyOwner {
        require(agentIdToAddress[agentId] == address(0), "Agent already registered");
        agents[wallet] = Agent({
            agentId:        agentId,
            wallet:         wallet,
            tradesExecuted: 0,
            feesEarned:     0,
            registeredAt:   block.timestamp,
            active:         true
        });
        agentIdToAddress[agentId] = wallet;
        agentList.push(wallet);
        emit AgentRegistered(wallet, agentId, block.timestamp);
    }

    function recordTrade(
        string calldata agentId,
        uint256 tradesExecuted,
        uint256 feesEarned
    ) external onlyOwner {
        address wallet = agentIdToAddress[agentId];
        require(wallet != address(0), "Agent not registered");
        agents[wallet].tradesExecuted = tradesExecuted;
        agents[wallet].feesEarned     = feesEarned;
        emit TradeRecorded(wallet, agentId, tradesExecuted, feesEarned);
    }

    function getAgent(string calldata agentId) external view returns (Agent memory) {
        address wallet = agentIdToAddress[agentId];
        return agents[wallet];
    }

    function getAgentCount() external view returns (uint256) {
        return agentList.length;
    }

    function getAllAgents() external view returns (Agent[] memory) {
        Agent[] memory result = new Agent[](agentList.length);
        for (uint256 i = 0; i < agentList.length; i++) {
            result[i] = agents[agentList[i]];
        }
        return result;
    }
}
