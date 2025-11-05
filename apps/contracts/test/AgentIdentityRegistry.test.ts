import { expect } from "chai";
import { ethers } from "hardhat";
import { AgentIdentityRegistry } from "../typechain-types";
import { SignerWithAddress } from "@nomicfoundation/hardhat-ethers/signers";

describe("AgentIdentityRegistry", function () {
  let identityRegistry: AgentIdentityRegistry;
  let owner: SignerWithAddress;
  let user1: SignerWithAddress;
  let user2: SignerWithAddress;

  beforeEach(async function () {
    [owner, user1, user2] = await ethers.getSigners();

    const AgentIdentityRegistry = await ethers.getContractFactory("AgentIdentityRegistry");
    identityRegistry = await AgentIdentityRegistry.deploy();
    await identityRegistry.waitForDeployment();
  });

  describe("Agent Registration", function () {
    it("Should register a new agent and mint NFT", async function () {
      const name = "TestAgent";
      const description = "A test agent";
      const capabilities = ["coding", "testing"];
      const endpoint = "https://agent.example.com/api";
      const metadataURI = "ipfs://QmTest123";

      const tx = await identityRegistry.connect(user1).registerAgent(
        name,
        description,
        capabilities,
        endpoint,
        metadataURI
      );

      const receipt = await tx.wait();
      expect(receipt).to.not.be.null;

      // Check that NFT was minted (tokenId should be 1)
      const tokenId = 1;
      expect(await identityRegistry.ownerOf(tokenId)).to.equal(user1.address);

      // Check agent card
      const agentCard = await identityRegistry.getAgentCard(tokenId);
      expect(agentCard.name).to.equal(name);
      expect(agentCard.description).to.equal(description);
      expect(agentCard.capabilities).to.deep.equal(capabilities);
      expect(agentCard.endpoint).to.equal(endpoint);
      expect(agentCard.isActive).to.be.true;
    });

    it("Should not allow duplicate endpoints", async function () {
      const endpoint = "https://agent.example.com/api";

      await identityRegistry.connect(user1).registerAgent(
        "Agent1",
        "First agent",
        ["capability1"],
        endpoint,
        "ipfs://QmTest1"
      );

      await expect(
        identityRegistry.connect(user2).registerAgent(
          "Agent2",
          "Second agent",
          ["capability2"],
          endpoint,
          "ipfs://QmTest2"
        )
      ).to.be.revertedWith("Endpoint already registered");
    });

    it("Should require at least one capability", async function () {
      await expect(
        identityRegistry.connect(user1).registerAgent(
          "Agent",
          "Description",
          [],
          "https://endpoint.com",
          "ipfs://QmTest"
        )
      ).to.be.revertedWith("Must have at least one capability");
    });

    it("Should emit AgentRegistered event", async function () {
      await expect(
        identityRegistry.connect(user1).registerAgent(
          "TestAgent",
          "Description",
          ["capability"],
          "https://endpoint.com",
          "ipfs://QmTest"
        )
      )
        .to.emit(identityRegistry, "AgentRegistered")
        .withArgs(1, "https://endpoint.com", user1.address, "TestAgent");
    });
  });

  describe("Agent Discovery", function () {
    beforeEach(async function () {
      // Register multiple agents with different capabilities
      await identityRegistry.connect(user1).registerAgent(
        "CodingAgent",
        "Agent for coding",
        ["coding", "debugging"],
        "https://agent1.com",
        "ipfs://QmTest1"
      );

      await identityRegistry.connect(user1).registerAgent(
        "TestingAgent",
        "Agent for testing",
        ["testing", "qa"],
        "https://agent2.com",
        "ipfs://QmTest2"
      );

      await identityRegistry.connect(user2).registerAgent(
        "FullstackAgent",
        "Agent for fullstack",
        ["coding", "testing", "deployment"],
        "https://agent3.com",
        "ipfs://QmTest3"
      );
    });

    it("Should find agents by capability", async function () {
      const codingAgents = await identityRegistry.findAgentsByCapability("coding");
      expect(codingAgents.length).to.equal(2);
      expect(codingAgents).to.include(1n);
      expect(codingAgents).to.include(3n);

      const testingAgents = await identityRegistry.findAgentsByCapability("testing");
      expect(testingAgents.length).to.equal(2);
      expect(testingAgents).to.include(2n);
      expect(testingAgents).to.include(3n);
    });

    it("Should get agents by owner", async function () {
      const user1Agents = await identityRegistry.getAgentsByOwner(user1.address);
      expect(user1Agents.length).to.equal(2);

      const user2Agents = await identityRegistry.getAgentsByOwner(user2.address);
      expect(user2Agents.length).to.equal(1);
    });
  });

  describe("Agent Management", function () {
    let tokenId: number;

    beforeEach(async function () {
      const tx = await identityRegistry.connect(user1).registerAgent(
        "TestAgent",
        "Description",
        ["capability1"],
        "https://endpoint.com",
        "ipfs://QmTest"
      );
      await tx.wait();
      tokenId = 1;
    });

    it("Should update agent card", async function () {
      await identityRegistry.connect(user1).updateAgentCard(
        tokenId,
        "New description",
        ["capability2", "capability3"],
        "ipfs://QmNewTest"
      );

      const agentCard = await identityRegistry.getAgentCard(tokenId);
      expect(agentCard.description).to.equal("New description");
      expect(agentCard.capabilities).to.deep.equal(["capability2", "capability3"]);
    });

    it("Should not allow non-owner to update", async function () {
      await expect(
        identityRegistry.connect(user2).updateAgentCard(
          tokenId,
          "New description",
          ["capability2"],
          "ipfs://QmNewTest"
        )
      ).to.be.revertedWith("Not agent owner");
    });

    it("Should deactivate agent", async function () {
      await identityRegistry.connect(user1).deactivateAgent(tokenId);

      const agentCard = await identityRegistry.getAgentCard(tokenId);
      expect(agentCard.isActive).to.be.false;
    });

    it("Should reactivate agent", async function () {
      await identityRegistry.connect(user1).deactivateAgent(tokenId);
      await identityRegistry.connect(user1).reactivateAgent(tokenId);

      const agentCard = await identityRegistry.getAgentCard(tokenId);
      expect(agentCard.isActive).to.be.true;
    });
  });

  describe("NFT Transfer", function () {
    it("Should update owner on transfer", async function () {
      await identityRegistry.connect(user1).registerAgent(
        "TestAgent",
        "Description",
        ["capability1"],
        "https://endpoint.com",
        "ipfs://QmTest"
      );

      const tokenId = 1;

      // Transfer to user2
      await identityRegistry.connect(user1).transferFrom(user1.address, user2.address, tokenId);

      // Check new owner
      expect(await identityRegistry.ownerOf(tokenId)).to.equal(user2.address);

      const agentCard = await identityRegistry.getAgentCard(tokenId);
      expect(agentCard.owner).to.equal(user2.address);

      // Check owner mappings
      const user1Agents = await identityRegistry.getAgentsByOwner(user1.address);
      expect(user1Agents.length).to.equal(0);

      const user2Agents = await identityRegistry.getAgentsByOwner(user2.address);
      expect(user2Agents).to.include(1n);
    });
  });

  describe("Statistics", function () {
    it("Should track total agents", async function () {
      expect(await identityRegistry.totalAgents()).to.equal(0);

      await identityRegistry.connect(user1).registerAgent(
        "Agent1",
        "Description",
        ["capability1"],
        "https://endpoint1.com",
        "ipfs://QmTest1"
      );

      expect(await identityRegistry.totalAgents()).to.equal(1);

      await identityRegistry.connect(user2).registerAgent(
        "Agent2",
        "Description",
        ["capability2"],
        "https://endpoint2.com",
        "ipfs://QmTest2"
      );

      expect(await identityRegistry.totalAgents()).to.equal(2);
    });
  });
});

