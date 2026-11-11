import {loadEffectiveCatalogueSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
process.stdout.write(JSON.stringify(loadEffectiveCatalogueSync(process.argv[2]||process.cwd())));
