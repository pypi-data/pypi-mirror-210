from ding.model.template.pdqn import *
obs_dim, seq_len, bs = 128, 64, 32
action_mask = [[0,0,0,0],[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
action_space = {"action_type_shape": torch.LongTensor([5]), "action_args_shape": torch.LongTensor([4])}

pdqn_model = PDQN(obs_dim, EasyDict(action_space), multi_pass=True, action_mask=action_mask)

obs = torch.rand(seq_len, bs, obs_dim)
obs = obs.view(-1, obs_dim)
action_args = pdqn_model.forward(obs, "compute_continuous")
action_type = pdqn_model.forward({"state": obs, "action_args": action_args["action_args"]}, "compute_discrete")
action_args["action_args"] = action_args["action_args"].view(seq_len, bs, -1)
action_type["logit"] = action_type["logit"].view(seq_len, bs, -1)
