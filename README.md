## Type Language Object

> Reader of [binary serialized](https://core.telegram.org/mtproto/serialize) Type Language Schema

### Example of result in the end of reading TLO

<p align="center">
    <img src="https://raw.githubusercontent.com/MarshalX/tlo/main/.github/resources/demo.gif" alt="demo">
</p>

### Declaimer

This code has not been tested sufficiently. 
It's a rewritten version of original reader in C++.
If you are going to use this for code generation, 
please do additional tests. 
Recheck my implementation for errors and so on.

### Context

The [Type Language (TL)](https://core.telegram.org/mtproto/TL) was
invented many years ago. It was originally used in [VK](https://vk.com/),
and now in [Telegram](https://telegram.org). 
The creators of this language invented and 
wrote all the necessary tools to work with it.
For example, a [parser of the language](https://github.com/vysheng/tl-parser)
and its [binary format](https://core.telegram.org/mtproto/serialize)
for serialization was developed.

### What is this for?

To work with TL Schemes using OOP. To generate the client MTProto code using
official TL parsers and binary formats.

Many Open Source MTProto client use their own implementation of parsers, 
which are not ultimatum. They are hardcoded for their minimal task.

Hardcode is not the way of Telegram. Official Telegram's Open Source projects 
take the right approach. So, for example, [tdlib](https://github.com/tdlib/td)
generates several interfaces for different languages and this is how it looks:

Raw TL Schema -> Tl Parser -> binary TL Object -> **TLO reader** -> code generator.

| Step name | Description |
| --------- | ----------- |
| Raw TL Schema  | Can be founded [here](https://core.telegram.org/schema) and in official Telegram repositories of client ([tdesktop/Telegram/Resources/tl](https://github.com/telegramdesktop/tdesktop/tree/dev/Telegram/Resources/tl), [tdlib/generate/scheme](https://github.com/tdlib/td/tree/master/td/generate/scheme)).  |
| Tl Parser | Official TL parser written in C++. Now it's a part of [tdlib/td/generate/tl-parser](https://github.com/tdlib/td/tree/master/td/generate/tl-parser). In the input it takes raw TL schema file. The output is TLO file. |
| binary TL Object | The output of Tl Parser. |
| **TLO reader** | **This repository contains implementation of it in Python and JavaScript.** Reader of binary file. Provide access to combinators, types, functions, arguments and so on via Object Oriented Programming. |
| code generator | Any code generator. In [tdlib/td/generate](https://github.com/tdlib/td/tree/master/td/generate) there is generator for C++, JNI, .NET and JSON interfaces. |

### Installing

#### For Python
```bash
pip install tlo
```

#### ~~For JavaScript~~ Work in progress
```bash
npm install tlo
```

### Usage

You can find TLO files for tests [here](https://github.com/MarshalX/tlo/tree/main/tlo_for_tests).

#### Python (3.6+)
```python
from tlo import read_tl_config_from_file, read_tl_config


# use read_tl_config(data) to pass bytes directly
config = read_tl_config_from_file('td_api.tlo')
```

#### ~~JavaScript~~ Work in progress
```javascript
import {read_tl_config_from_file, read_tl_config} from 'tlo';


// use read_tl_config(data) to pass bytes directly
const config = read_tl_config_from_file('td_api.tlo')
```

### Licence

MIT License
