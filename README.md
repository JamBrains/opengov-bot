# ChaosDAO Governance bot

![GitHub License](https://img.shields.io/github/license/ChaosDAO-org/InternalGov-2.0)
![Supported](https://img.shields.io/badge/python-3.9.5%2B-blue)
![GitHub commits since latest release](https://img.shields.io/github/commits-since/ChaosDAO-org/InternalGov-2.0/latest)  

A dedicated discussion forum within your Discord server, specifically designed to facilitate thoughtful and constructive conversations around ongoing proposals. This interactive platform empowers members to openly share their insights, perspectives, and opinions on each referendum prior to the submission of an official vote by the designated proxy account on behalf of the collective or DAO.

The primary objective of this forum is to foster an environment of collaboration and informed decision-making, ensuring that every voice within the community is acknowledged and taken into consideration. By harnessing the collective wisdom of your community, you can make well-informed decisions that truly represent the best interests of the entire group.

We encourage everyone to actively participate in these discussions, as your input and feedback are invaluable in shaping the direction and outcomes of your collectives endeavors. Together, we can forge a stronger, more unified community that thrives on the principles of transparency, cooperation, and shared vision.

![alt text](https://i.imgur.com/Ogg29qC.png)

---

## Initial setup
- [Discord API key, Server & Forum ID](https://github.com/ChaosDAO-org/InternalGov-2.0/wiki/1.-Initial-Setup#discord-application-api-key)
- [Enabling your community server & creating a forum channel](https://github.com/ChaosDAO-org/InternalGov-2.0/wiki/2.-Forum-Channels#what-are-forum-channels)
- [Organising with categories](https://github.com/ChaosDAO-org/InternalGov-2.0/wiki/3.-Channel-Categories#adding-a-category)
- [FAQ](https://github.com/ChaosDAO-org/InternalGov-2.0/wiki/99.-FAQ)

  
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/SYnpgcgfDsA/0.jpg)](https://www.youtube.com/watch?v=SYnpgcgfDsA)
---

### [.env.sample](https://raw.githubusercontent.com/ChaosDAO-org/InternalGov-2.0/main/.env.sample)
#### This file should be renamed from .env.sample -> .env

---

## Installing prerequisite libraries / tooling
```shell
cd InternalGov-2.0
pip3 install -r requirements.txt
```

##### Installing PM2 (Process Manager)
###### PM2 is a daemon process manager that will help you manage and keep your application/bot online 24/7  
https://pm2.keymetrics.io/docs/usage/quick-start/  

`npm install pm2 -g`

###### Daemonizing the bot to run 24/7 with PM2
```shell
# change directory
cd InternalGov-2.0/bot/

# test before daemonizing (review log file in /data/logs/governance_bot.log)
python3 main.py

# daemonize
pm2 start main.py --name polkadot_gov --interpreter python3
pm2 save

# stopping/starting & restarting pm2 process
pm2 stop polkadot_gov
pm2 start polkadot_gov
pm2 restart polkadot_gov

# list process(s); App name, ID, Mode, Status, CPU, Memory, Uptime, Restarts
pm2 list
```


###### Running docker version

```shell
# Build the image
docker build -t internal-gov-2 .

# Create volume for data
docker volume create internal-gov-2-data

# Run (+ restart) and mount data volume
docker run -d \
  --name internal-gov-2 \
  --mount source=internal-gov-2-data,target=/app/data \
  --restart always \
  internal-gov-2

  docker run -d   --name internal-gov-2   -v ./data:/app/data   -v ./.env:/app/.env   --restart always   internal-gov-2

# Copy .env file
docker cp .env internal-gov-2:/app/
```

---
## Autonomous voting
![alt text](https://i.imgur.com/5d0HJsY.png)  

When the bot votes is dictated by `/data/vote_periods`. Each origin of a proposal has its own setting on when the first vote should be made & second. A second vote will only be made if the result differs from the first vote. If the first vote is AYE and it remains AYE on the second period then no vote will be made on the network.  
[Polkadot vote periods](/data/vote_periods/polkadot.json)  
[Kusama vote periods](/data/vote_periods/kusama.json)


### vote settings
###### Kusama vote periods
| Role                | Decision Period (days) | Internal Vote Period (days) | Revote Period (days) |
|---------------------|------------------------|-----------------------------|----------------------|
| Root                | 14                     | 5                           | 10                   |
| WhitelistedCaller   | 14                     | 3                           | 10                   |
| StakingAdmin        | 14                     | 5                           | 10                   |
| Treasurer           | 14                     | 5                           | 10                   |
| LeaseAdmin          | 14                     | 5                           | 10                   |
| FellowshipAdmin     | 14                     | 5                           | 10                   |
| GeneralAdmin        | 14                     | 5                           | 10                   |
| AuctionAdmin        | 14                     | 5                           | 10                   |
| ReferendumCanceller | 7                      | 2                           | 4                    |
| ReferendumKiller    | 14                     | 2                           | 10                   |
| SmallTipper         | 7                      | 1                           | 4                    |
| BigTipper           | 7                      | 1                           | 4                    |
| SmallSpender        | 14                     | 5                           | 10                   |
| MediumSpender       | 14                     | 5                           | 10                   |
| BigSpender          | 14                     | 5                           | 10                   |
| WishForChange       | 14                     | 5                           | 10                   |
> Example:
> > A proposal is submitted with its origin designated as 'Treasurer'. Following a period of five days after its on-chain introduction, a vote is conducted in accordance with the predetermined internal outcome. Should there be a shift in the voting stance from 'AYE' to 'NAY', a subsequent vote will be executed on the tenth day of the proposal's on-chain presence. In instances where the initial decision remains unaltered and the proposal has aged ten days or more, no further on-chain voting action will be undertaken.

---

###### Polkadot vote periods
| Role                | Decision Period (days) | Internal Vote Period (days) | Revote Period (days) |
|---------------------|------------------------|-----------------------------|----------------------|
| Root                | 28                     | 7                           | 20                   |
| WhitelistedCaller   | 28                     | 2                           | 20                   |
| StakingAdmin        | 28                     | 7                           | 20                   |
| Treasurer           | 28                     | 7                           | 20                   |
| LeaseAdmin          | 28                     | 7                           | 20                   |
| FellowshipAdmin     | 28                     | 7                           | 20                   |
| GeneralAdmin        | 28                     | 7                           | 20                   |
| AuctionAdmin        | 28                     | 7                           | 20                   |
| ReferendumCanceller | 7                      | 2                           | 4                    |
| ReferendumKiller    | 28                     | 4                           | 20                   |
| SmallTipper         | 7                      | 2                           | 4                    |
| BigTipper           | 7                      | 2                           | 4                    |
| SmallSpender        | 28                     | 7                           | 20                   |
| MediumSpender       | 28                     | 7                           | 20                   |
| BigSpender          | 28                     | 7                           | 20                   |
| WishForChange       | 28                     | 7                           | 20                   |
> Example:
> > A proposal is submitted with its origin designated as 'AuctionAdmin'. Following a period of seven days after its on-chain introduction, a vote is conducted in accordance with the predetermined internal outcome. Should there be a shift in the voting stance from 'AYE' to 'NAY', a subsequent vote will be executed on the twentieth day of the proposal's on-chain presence. In instances where the initial decision remains unaltered and the proposal has aged ten days or more, no further on-chain voting action will be undertaken.

---

## Support
For assistance or inquiries, please refer to the following official channels of communication: 

| Platform | User   | UID/URL                                                                                                                                                                                      |
|----------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Telegram | n4droj | [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white&link=https://t.me/n4droj)](https://t.me/n4droj)                                  |
| Discord  | n4dro  | [![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white&link=https%3A%2F%2Fdiscord.gg%2FfGJe2AWkGe)](https://discord.com/invite/fGJe2AWkGe) |
| Twitter  | n4dro  | [![Twitter](https://img.shields.io/twitter/follow/N4DRO)](https://www.x.com/N4DRO)                                                                                                           |
