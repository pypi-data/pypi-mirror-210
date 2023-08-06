# ### find left neighbor or check if located inside gene
# ### chr_dict[contig][i] = (geneid, start, end, strand)
# ###############################################################################
# # case 1): there is no protein-coding gene on the same contig as the miRNA,
# # so there can be no neighbors (should only occur in highly fragmented
# # assemblies)
# if not chromo in ref_dict.keys():
#     print(
#         'WARNING: No protein-coding genes found on contig "{0}". '
#         'Synteny around {1} cannot be established.\n'
#         'Make sure that the contig identifiers of the miRNA input file '
#         'match the ones in the reference annotation file'
#             .format(chromo, mirid)
#     )
#     continue
#
# # case 2): miRNA is located left of the first gene and hence has no left
# # neighbor, the first gene is therefore by default the right neighbor
# if end < int(ref_dict[chromo][1][1]):
#     print(
#         'There is no left neighbor of {0}, since it is located at the '
#         'start of contig {1}.'.format(mirid, chromo)
#     )
#     print(
#         '{0} is the right neighbor of {1}.'
#             .format(ref_dict[chromo][1][0], mirid)
#     )
#     continue
#
# # case 3): miRNA is located right to the last gene, so the last gene is the
# # left neighbor and there cannot be a right neighbor
# elif start > int(ref_dict[chromo][len(ref_dict[chromo])][2]):
#     print(
#         '{0} is the left neighbor of {1}.'
#             .format(ref_dict[chromo][len(ref_dict[chromo])][0], mirid)
#     )
#     print(
#         'There is no right neighbor of {0}, since it is located at the'
#         ' end of contig {1}.'.format(mirid, chromo)
#     )
#     continue
#
# # case 4): miRNA is located either between two genes or overlapping with (an
# # intron of) a gene, either on the same or the opposite strand
# ###############################################################################
# else:
#     solved = False
#     for i, gene in enumerate(ref_dict[chromo]):
#         gene_data = ref_dict[chromo][gene]
#         # case 4.1): miRNA inside gene
#         if (
#                 start >= gene_data[1]
#                 and end <= gene_data[2]
#                 and strand == gene_data[3]
#         ):
#             solved = True
#             # c+=1
#             print(
#                 '{0} is located inside the gene {1}.'
#                     .format(mirid, gene_data[0])
#             )
#             ortho_hits = ortho_search(gene_data[0], ortho_dict)
#             for core_tax in ortho_hits:
#                 try:
#                     neighbor_dict[core_tax][mirid] = (
#                         ('inside', ortho_hits[core_tax])
#                     )
#                 except:
#                     neighbor_dict[core_tax] = (
#                         {mirid: ('inside', ortho_hits[core_tax])}
#                     )
#             break
#         # case 4.2): miRNA opposite of gene
#         elif (
#                 start >= gene_data[1]
#                 and end <= gene_data[2]
#                 and strand != gene_data[3]
#         ):
#             solved = True
#             print(
#                 '{0} is located opposite of the gene {1}.'
#                     .format(mirid, gene_data[0])
#             )
#             ortho_hits = ortho_search(gene_data[0], ortho_dict)
#             for core_tax in ortho_hits:
#                 try:
#                     neighbor_dict[core_tax][mirid] = (
#                         ('opposite', ortho_hits[core_tax])
#                     )
#                 except:
#                     neighbor_dict[core_tax] = (
#                         {mirid: ('opposite', ortho_hits[core_tax])}
#                     )
#             break
#         # case 4.3): miRNA between genes
#         elif (
#                 int(ref_dict[chromo][gene][2]) < start
#                 and ref_dict[chromo][gene + 1][1] > end
#         ):
#             solved = True
#             ###############################################################################
#             print(
#                 '{1} is the left neighbor of {2}.'
#                 .format(gene, ref_dict[chromo][gene][0], mirid)
#             )
#             print(
#                 '{1} is the right neighbor of {2}.'
#                 .format(gene, ref_dict[chromo][gene + 1][0], mirid)
#             )
#             left_hits = ortho_search(gene_data[0], ortho_dict)
#             right_hits = (
#                 ortho_search(ref_dict[chromo][gene + 1][0], ortho_dict)
#             )
#             # save only the hits where both genes have orthologs in a species
#             if left_hits:
#                 # print(left_hits)
#                 # print(right_hits)
#                 for taxon in left_hits:
#                     if taxon in right_hits:
#                         try:
#                             neighbor_dict[taxon][mirid] = (
#                                 (
#                                     'in-between',
#                                     [left_hits[taxon],
#                                      right_hits[taxon]]
#                                 )
#                             )
#                         except:
#                             neighbor_dict[taxon] = (
#                                 {mirid: (
#                                     'in-between',
#                                     [left_hits[taxon],
#                                      right_hits[taxon]]
#                                 )}
#                             )
#                     else:
#                         print('Orthologs were not found for both flanking genes')
#             break
#     if not solved:
#         print('Unable to resolve synteny for {}.'.format(mirid))
#
#
# ##########################################################################################
#
#         print('# Loading genome file')
#         fasta_path = core_dict[taxon]['genome']
#         core_gen_dict = '{}/core_genomes'.format(output)
#         if not os.path.isdir(core_gen_dict):
#             os.mkdir(core_gen_dict)
#         slink = '{}/slink_to_{}'.format(core_gen_dict, taxon)
#         try:
#             os.symlink(fasta_path, slink)
#         except FileExistsError:
#             pass
#         genome = pyfaidx.Fasta(slink)
#         print('Done')
#
#
# ##########################################################################################
# # print(mirna)
# style = neighbor_dict[taxon][mirna][0]
# if style == 'inside' or style == 'opposite':
#     print(f'# {mirna} location: {style} of gene')
#     try:
#         ortho_data = (
#             core_dict[neighbor_dict[taxon][mirna][1]]
#         )
#     except KeyError as e:
#         print('{} not found in annotation file.'.format(e))
#         continue
#     positions = list(
#         core_dict[ortho_data[0]][ortho_data[1]][1:4]
#     )
#     coordinates = [ortho_data[0]] + positions
#     seq = (
#         genome[coordinates[0]]
#         [coordinates[1] - 1:coordinates[2]].seq
#     )
#     # print(seq[0:10])
#     try:
#         mirna_dict[mirna][taxon] = seq
#     except KeyError:
#         mirna_dict[mirna] = {taxon: seq}
# ##########################################################################################
#
#     # Search for the coordinates of the orthologs and extract the sequences
#     for taxon in neighbor_dict:
#         # print('YOU MADE IT THIS FAR.')
#         for mirna in neighbor_dict[taxon]:
#
#             if style == 'in-between':
#                 print(f'# {mirna} location: between genes')
#                 try:
#                     left_data = (
#                         core_dict[neighbor_dict[taxon][mirna][1][0]]
#                     )
#                     right_data = (
#                         core_dict[neighbor_dict[taxon][mirna][1][1]]
#                     )
#                 except KeyError as e:
#                     print('{} not found in annotation file.'.format(e))
#                     continue
#                 # Test to see if the two orthologs are themselves neighbors where their
#                 # distance cannot be larger than the selected mgi value. This accounts
#                 # for insertions in the core species.
#                 # TODO: Apply mgi also to the reference species to account for insertions
#                 # in the reference.
#                 #                 print(f'left_data: {left_data}')
#                 #                 print(f'right_data: {right_data}')
#                 if (
#                         left_data[0] == right_data[0]
#                         and abs(left_data[1] - right_data[1]) <= mgi
#                 ):
#                     # Determine which sequence to include for the synteny-based ortholog search
#                     # depending on the order of orthologs. The order of the orthologs in the core
#                     # species might be inverted compared to that in the reference species.
#                     ###############################################################################
#                     if left_data[1] < right_data[1]:
#                         # print('left')
#                         # print(core_gtf_dict[left_data[0]][left_data[1]])
#                         # print(core_gtf_dict[right_data[0]][right_data[1]])
#                         contig = left_data[0]
#                         # print(contig)
#                         seq_start = int(
#                             core_dict[left_data[0]][left_data[1]][2]
#                         )
#                         # print(seq_start)
#                         seq_end = (
#                             core_dict[right_data[0]][right_data[1]][1]
#                         )
#                         # print(seq_end)
#                         seq = genome[contig][seq_start - 1:seq_end].seq
#                         try:
#                             mirna_dict[mirna][taxon] = seq
#                         except:
#                             mirna_dict[mirna] = {taxon: seq}
#                     elif right_data[1] < left_data[1]:
#                         # print('right')
#                         # print(core_gtf_dict[left_data[0]][left_data[1]])
#                         # print(core_gtf_dict[right_data[0]][right_data[1]])
#                         contig = left_data[0]
#                         # print(contig)
#                         # seq_start = int(
#                         #     core_gtf_dict[left_data[0]][left_data[1]][2]
#                         # )
#                         # print(seq_start)
#                         # seq_end = (
#                         #     core_gtf_dict[right_data[0]][right_data[1]][1]
#                         # )
#                         seq_start = int(
#                             core_dict[right_data[0]][right_data[1]][2]
#                         )
#                         # print(seq_start)
#                         seq_end = (
#                             core_dict[left_data[0]][left_data[1]][1]
#                         )
#                         # print(seq_end)
#                         seq = genome[contig][seq_start - 1:seq_end].seq
#                         try:
#                             mirna_dict[mirna][taxon] = seq
#                         except:
#                             mirna_dict[mirna] = {taxon: seq}
#                     print('Synteny fulfilled.')
#                 else:
#                     print(
#                         'No shared synteny for {} in {}.'
#                             .format(mirna, taxon)
#                     )
#                     continue
#                     # print(left_data)
#                     # print(right_data)
#             else:
#                 print('## Neither inside, opposite, nor in-between')
#                 # print(neighbor_dict[taxon][mirna])
#                 continue
#             print('Candidate region found')
#
#             ##########################################################################################
#             # Write output file
#             for mirna in mirna_dict:
#                 # print('{0}/{1}/{1}.fa'.format(output, mirna))
#                 with open('{0}/{1}/{1}.fa'.format(output, mirna), 'w') as outfile:
#                     for core_taxon in mirna_dict[mirna]:
#                         outfile.write(
#                             '>{0}\n{1}\n'
#                                 .format(core_taxon, mirna_dict[mirna][core_taxon])
#                         )
#             if not mirna_dict:
#                 print('\nWARNING: No syntenic regions found in the core species')
#             ##########################################################################################
#
#             # skip_file = '{}/not_found_in_ref.fa'.format(o_path)
#             # if not os.path.isfile(skip_file):
#             #     with open(skip_file, 'w') as of:
#             #         of.write('>{}\n{}\n'.format(mirna, seq))
#             # else:
#             #     with open(skip_file, 'a') as of:
#             #         of.write('>{}\n{}\n'.format(mirna, seq))
#             # return None
#
#     ##########################################################################################
#     ##### Collect best hit for each core set species if it is within the accepted bit score range
#
#     core_dict = {}
#     result_list = results.split('\n')
#     # print(result_list)
#     if result_list:
#         #print(result_list)
#         for hit in result_list:
#             if hit:
#                 hit_data = hit.split()
#                 # print(hit_data)
#                 # print(f'hit bitscore: {hit_data[2]}')
#                 # print(f'you needed: {0.5*ref_bit_score}')
#                 # print(f'and you got: {hit_data[2]}')
#                 if (
#                     not hit_data[0] in core_dict
#                     and float(hit_data[2]) >= 0.5*ref_bit_score
#                 ):
#                     core_dict[hit_data[0]] = hit
#                     print(f'pre-miRNA candidate found for {hit_data[0]}! ({hit_data[2]}/{0.5*ref_bit_score})')
#                     break
#                 else:
#                     print(f'Syntenic candidate region BLAST hit below reference bit score threshold ({hit_data[2]}/{0.5*ref_bit_score})')
#
#     if len(core_dict) == 0:
#         print('WARNING: No region in the core species scored above the reference bit score threshold')
#
#         ##### Re-BLAST #####
#         print('\n### Starting reciprocal BLAST search.')
#         accept_dict = {}
#         for species in core_dict.keys():
#             print(f'# {species}')
#             # Make sure to eliminate gaps
#             candidate_seq = core_dict[species].split()[3].replace('-', '')
#             reblastn_cmd = (
#                 'blastn -num_threads {c} -task blastn -dust {dust} -db {ref_blastdb} -outfmt \"6'
#                 ' sseqid sstart send evalue bitscore\"'
#             )
#             reblastn = sp.Popen(
#                 reblastn_cmd, shell=True, stdin=sp.PIPE,
#                 stdout=sp.PIPE, stderr=sp.STDOUT, encoding='utf8'
#             )
#             reresults, reerr = reblastn.communicate(candidate_seq)
#             if reerr:
#                 print(reerr)
#                 sys.exit()
#
#             # Check if reverse hit overlaps with reference miRNA
#             if reresults:
#                 first_hit = reresults.split('\n')[0].split()
#                 rchr = first_hit[0]
#                 rstart = int(first_hit[1])
#                 rend = int(first_hit[2])
#                 if rchr == mchr:
#                     # print('Same chromosome.')
#                     if (
#                             (rstart <= mstart and mstart <= rend)
#                             or (rstart <= mend and mend <= rend)
#                     ):
#                         # first within second
#                         print('Reciprocity fulfilled.')
#                         accept_dict[species] = core_dict[species]
#                     elif (
#                             (mstart <= rstart and rstart <= mend)
#                             or (mstart <= rend and rend <= mend)
#                     ):
#
#                         # second within first
#                         print('Reciprocity fulfilled.')
#                         accept_dict[species] = core_dict[species]
#                     else:
#                         print('Reciprocity unfulfilled.')
#                 else:
#                     print('Hit on chromosome {}, expected {}'.format(rchr, mchr))
#             else:
#                 print(
#                     'No reverse hit for {}. Reciprocity unfulfilled.'
#                         .format(mirid)
#
#
#
#     with open(corefile, 'w') as outfile:
#         outfile.write('>{}\n{}\n'.format(mirid, preseq))
#         print('\n### Starting Alignment')
#         # print('>{}\n{}'.format(mirid, preseq))
#         for accepted in accept_dict:
#             # print('>{}\n{}'.format(accepted, core_dict[accepted].split('\t')[3]))
#             outfile.write(
#                 '>{}\n{}\n'
#                     .format(accepted, accept_dict[accepted].split('\t')[3])
#                     .replace('-', '')