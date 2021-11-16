//SPDX-License-Identifier: MIT 
pragma solidity >=0.7.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase{
    address payable[] players;
    uint256 usdEntryFee;
    address payable recenetWinner;
    uint256 recentRandomNumber;
    AggregatorV3Interface internal ethUsd_priceFeed;
    enum LOTTER_STATE{
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTER_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyhash;

    constructor(address _price_feed_address,address _vrf_coordinator, address _link, uint256 _fee, bytes32 _keyhash) VRFConsumerBase(_vrf_coordinator, _link) {
        // Unit of measurement in wei 
        usdEntryFee = uint256(50 * 10**18);
        ethUsd_priceFeed = AggregatorV3Interface(_price_feed_address);
        lottery_state = LOTTER_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }
        // 50$ minimum
    
    function getEnteranceFee() public view returns(uint256){
        (, int256 ethPrice ,,,) = ethUsd_priceFeed.latestRoundData(); // from the documentation we saw that it had 8 decimal places
        uint256 adjustedPrice = uint256(ethPrice) * 10**10; // 18 decimals
        // we want to return the value in wei
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }
    function enterLottery() public payable{
        require(lottery_state == LOTTER_STATE.OPEN);
        require(msg.value >= getEnteranceFee(), "Not enough funds");
        players.push(payable(msg.sender));
    }
    function startLottery() public onlyOwner{
        require(lottery_state == LOTTER_STATE.CLOSED, "Can't start a new lottery yet");
        lottery_state = LOTTER_STATE.OPEN;
    }
    function endLottery() public onlyOwner{
        require(lottery_state == LOTTER_STATE.OPEN, "Can't end a lottery that is not open");
        lottery_state = LOTTER_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee);
    }
    function fulfillRandomness(bytes32 requestId, uint256 _randomness) internal override{
        require(lottery_state == LOTTER_STATE.CALCULATING_WINNER, "Can't fullfill randomness for a lottery that is not calculating");
        require(_randomness > 0, "Randomness must be greater than 0");

        uint256 indexOfWinner = _randomness % players.length;
        recenetWinner = players[indexOfWinner];
        recenetWinner.transfer(address(this).balance);

        // reset players
        players = new address payable[](0);
        lottery_state = LOTTER_STATE.CLOSED;
        recentRandomNumber = _randomness;
    }
}